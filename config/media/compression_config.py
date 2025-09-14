"""
Compression Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Compression Configuration Module
import asyncio

==========================================

Enterprise-grade compression configuration for the Ainflue platform.
Comprehensive video, audio, and image compression with advanced algorithms,
quality optimization, and performance tuning for content delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import math

class CompressionAlgorithm(str, Enum):
    """Compression algorithms"""
    # Video algorithms
    H264 = "h264"
    H265 = "h265"           # HEVC
    VP8 = "vp8"
    VP9 = "vp9"
    AV1 = "av1"             # Next-gen
    MPEG2 = "mpeg2"
    MPEG4 = "mpeg4"
    
    # Audio algorithms
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    FLAC = "flac"           # Lossless
    
    # Image algorithms
    JPEG = "jpeg"
    WEBP = "webp"
    AVIF = "avif"           # Next-gen
    HEIF = "heif"           # High efficiency
    PNG = "png"
    JPEG2000 = "jpeg2000"
    
    # General algorithms
    GZIP = "gzip"
    BROTLI = "brotli"
    ZSTD = "zstd"           # Facebook's Zstandard
    LZ4 = "lz4"             # Ultra-fast
    LZMA = "lzma"           # High compression

class CompressionMode(str, Enum):
    """Compression modes"""
    LOSSLESS = "lossless"           # No quality loss
    LOSSY = "lossy"                 # Quality loss allowed
    NEAR_LOSSLESS = "near_lossless" # Minimal quality loss
    ADAPTIVE = "adaptive"           # Adaptive based on content
    PROGRESSIVE = "progressive"     # Progressive encoding

class CompressionPreset(str, Enum):
    """Compression presets"""
    ULTRA_FAST = "ultra_fast"       # Maximum speed, lower compression
    VERY_FAST = "very_fast"         # Very fast, good compression
    FAST = "fast"                   # Fast, balanced
    MEDIUM = "medium"               # Balanced speed/compression
    SLOW = "slow"                   # Slower, better compression
    VERY_SLOW = "very_slow"         # Very slow, high compression
    ULTRA_SLOW = "ultra_slow"       # Maximum compression

class CompressionTarget(str, Enum):
    """Compression targets"""
    WEB_STREAMING = "web_streaming"     # Web streaming optimization
    MOBILE_STREAMING = "mobile_streaming" # Mobile optimization
    BROADCAST = "broadcast"             # Broadcast quality
    ARCHIVE = "archive"                 # Long-term storage
    DOWNLOAD = "download"               # Download optimization
    SOCIAL_MEDIA = "social_media"       # Social platforms
    EMAIL = "email"                     # Email attachments
    MESSAGING = "messaging"             # Messaging apps

class QualityMetric(str, Enum):
    """Quality metrics"""
    PSNR = "psnr"                   # Peak Signal-to-Noise Ratio
    SSIM = "ssim"                   # Structural Similarity Index
    VMAF = "vmaf"                   # Video Multimethod Assessment Fusion
    LPIPS = "lpips"                 # Learned Perceptual Image Patch Similarity
    DSSIM = "dssim"                 # Structural Dissimilarity
    BUTTERAUGLI = "butteraugli"     # Psychovisual similarity
    MSE = "mse"                     # Mean Squared Error

@dataclass
class CompressionQualitySettings:
    """Compression quality settings"""
    target_quality: float           # Target quality score (0-100)
    min_quality: float             # Minimum acceptable quality
    max_quality: float             # Maximum quality (for lossy)
    quality_metric: QualityMetric  # Quality measurement method
    
    # Rate control
    target_bitrate_kbps: Optional[int] = None    # Target bitrate
    max_bitrate_kbps: Optional[int] = None       # Maximum bitrate
    min_bitrate_kbps: Optional[int] = None       # Minimum bitrate
    
    # Advanced settings
    constant_quality: bool = False               # Constant quality mode
    variable_bitrate: bool = True                # Variable vs constant bitrate
    two_pass_encoding: bool = False              # Two-pass encoding
    look_ahead: int = 0                         # Look-ahead frames
    
    # Perceptual optimization
    perceptual_optimization: bool = True         # Perceptual quality optimization
    psychovisual_tuning: bool = True            # Psychovisual tuning
    content_adaptive: bool = True               # Content-adaptive encoding
    
    def calculate_quality_score(self, compressed_size: int, original_size: int, 
                               measured_quality: float) -> float:
        """Calculate overall quality score"""
        # Compression ratio (higher is better for compression)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        # Normalize compression ratio (assume 10:1 is excellent)
        compression_score = min(compression_ratio / 10.0, 1.0) * 100
        
        # Weighted score: 70% quality, 30% compression
        overall_score = (measured_quality * 0.7) + (compression_score * 0.3)
        
        return min(overall_score, 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "target_quality": self.target_quality,
            "min_quality": self.min_quality,
            "max_quality": self.max_quality,
            "quality_metric": self.quality_metric.value,
            "target_bitrate_kbps": self.target_bitrate_kbps,
            "max_bitrate_kbps": self.max_bitrate_kbps,
            "min_bitrate_kbps": self.min_bitrate_kbps,
            "constant_quality": self.constant_quality,
            "variable_bitrate": self.variable_bitrate,
            "two_pass_encoding": self.two_pass_encoding,
            "look_ahead": self.look_ahead,
            "perceptual_optimization": self.perceptual_optimization,
            "psychovisual_tuning": self.psychovisual_tuning,
            "content_adaptive": self.content_adaptive
        }

@dataclass
class VideoCompressionProfile:
    """Video compression profile"""
    profile_id: str
    name: str
    description: str
    
    # Algorithm settings
    algorithm: CompressionAlgorithm
    mode: CompressionMode
    preset: CompressionPreset
    target: CompressionTarget
    
    # Quality settings
    quality_settings: CompressionQualitySettings
    
    # Resolution settings
    resolution_width: int
    resolution_height: int
    maintain_aspect_ratio: bool = True
    allow_upscaling: bool = False
    
    # Frame rate settings
    target_fps: float = 30.0
    max_fps: float = 60.0
    adaptive_fps: bool = True
    
    # Advanced codec settings
    gop_size: int = 60               # Group of Pictures size
    b_frames: int = 2                # B-frames count
    ref_frames: int = 3              # Reference frames
    
    # Hardware acceleration
    hardware_acceleration: bool = False
    gpu_encoding: bool = False
    parallel_processing: bool = True
    
    # Content-specific settings
    motion_estimation: str = "hex"    # Motion estimation algorithm
    motion_threshold: float = 0.5     # Motion detection threshold
    scene_change_detection: bool = True
    noise_reduction: bool = False
    grain_synthesis: bool = False     # Film grain synthesis
    
    # Performance settings
    threads: int = 0                  # 0 = auto
    thread_type: str = "frame"        # frame, slice
    
    # Output settings
    pixel_format: str = "yuv420p"     # Pixel format
    color_space: str = "bt709"        # Color space
    color_range: str = "tv"           # tv, pc
    
    # Metadata
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def calculate_target_bitrate(self, duration_seconds: float, 
                                target_size_mb: float) -> int:
        """Calculate target bitrate for desired file size"""
        target_size_bits = target_size_mb * 8 * 1024 * 1024
        return int(target_size_bits / duration_seconds / 1000)  # kbps
    
    def estimate_compressed_size(self, duration_seconds: float) -> float:
        """Estimate compressed file size in MB"""
        if self.quality_settings.target_bitrate_kbps:
            size_bits = self.quality_settings.target_bitrate_kbps * 1000 * duration_seconds
            return size_bits / (8 * 1024 * 1024)  # Convert to MB
        return 0.0
    
    def get_complexity_score(self) -> int:
        """Get encoding complexity score (1-10)"""
        complexity = 1
        
        # Algorithm complexity
        if self.algorithm in [CompressionAlgorithm.H265, CompressionAlgorithm.AV1]:
            complexity += 3
        elif self.algorithm in [CompressionAlgorithm.VP9]:
            complexity += 2
        elif self.algorithm in [CompressionAlgorithm.H264]:
            complexity += 1
        
        # Preset complexity
        preset_complexity = {
            CompressionPreset.ULTRA_FAST: 0,
            CompressionPreset.VERY_FAST: 1,
            CompressionPreset.FAST: 2,
            CompressionPreset.MEDIUM: 3,
            CompressionPreset.SLOW: 4,
            CompressionPreset.VERY_SLOW: 5,
            CompressionPreset.ULTRA_SLOW: 6
        }
        complexity += preset_complexity.get(self.preset, 3)
        
        # Two-pass encoding
        if self.quality_settings.two_pass_encoding:
            complexity += 2
        
        return min(complexity, 10)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "algorithm": self.algorithm.value,
            "mode": self.mode.value,
            "preset": self.preset.value,
            "target": self.target.value,
            "quality_settings": self.quality_settings.to_dict(),
            "resolution": f"{self.resolution_width}x{self.resolution_height}",
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "maintain_aspect_ratio": self.maintain_aspect_ratio,
            "allow_upscaling": self.allow_upscaling,
            "target_fps": self.target_fps,
            "max_fps": self.max_fps,
            "adaptive_fps": self.adaptive_fps,
            "gop_size": self.gop_size,
            "b_frames": self.b_frames,
            "ref_frames": self.ref_frames,
            "hardware_acceleration": self.hardware_acceleration,
            "gpu_encoding": self.gpu_encoding,
            "parallel_processing": self.parallel_processing,
            "motion_estimation": self.motion_estimation,
            "motion_threshold": self.motion_threshold,
            "scene_change_detection": self.scene_change_detection,
            "noise_reduction": self.noise_reduction,
            "grain_synthesis": self.grain_synthesis,
            "threads": self.threads,
            "thread_type": self.thread_type,
            "pixel_format": self.pixel_format,
            "color_space": self.color_space,
            "color_range": self.color_range,
            "complexity_score": self.get_complexity_score(),
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class AudioCompressionProfile:
    """Audio compression profile"""
    profile_id: str
    name: str
    description: str
    
    # Algorithm settings
    algorithm: CompressionAlgorithm
    mode: CompressionMode
    preset: CompressionPreset
    target: CompressionTarget
    
    # Quality settings
    target_bitrate_kbps: int
    sample_rate_hz: int             # 44100, 48000, 96000
    channels: int                   # 1=mono, 2=stereo, 6=5.1, 8=7.1
    bit_depth: int = 16            # 16, 24, 32
    
    # Advanced settings
    variable_bitrate: bool = True
    joint_stereo: bool = True       # Joint stereo encoding
    psychoacoustic_model: int = 2   # Psychoacoustic model version
    
    # Audio processing
    dynamic_range_compression: bool = False
    noise_reduction: bool = False
    normalize_audio: bool = False
    high_frequency_cutoff: Optional[int] = None  # Hz
    low_frequency_cutoff: Optional[int] = None   # Hz
    
    # Performance settings
    encoding_quality: int = 5       # 0-9, higher = better quality
    
    # Metadata
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def calculate_file_size(self, duration_seconds: float) -> float:
        """Calculate estimated file size in MB"""
        size_bits = self.target_bitrate_kbps * 1000 * duration_seconds
        return size_bits / (8 * 1024 * 1024)  # Convert to MB
    
    def get_quality_level(self) -> str:
        """Get quality level description"""
        if self.target_bitrate_kbps >= 320:
            return "Very High"
        elif self.target_bitrate_kbps >= 192:
            return "High"
        elif self.target_bitrate_kbps >= 128:
            return "Good"
        elif self.target_bitrate_kbps >= 96:
            return "Standard"
        else:
            return "Low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "algorithm": self.algorithm.value,
            "mode": self.mode.value,
            "preset": self.preset.value,
            "target": self.target.value,
            "target_bitrate_kbps": self.target_bitrate_kbps,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "variable_bitrate": self.variable_bitrate,
            "joint_stereo": self.joint_stereo,
            "psychoacoustic_model": self.psychoacoustic_model,
            "dynamic_range_compression": self.dynamic_range_compression,
            "noise_reduction": self.noise_reduction,
            "normalize_audio": self.normalize_audio,
            "high_frequency_cutoff": self.high_frequency_cutoff,
            "low_frequency_cutoff": self.low_frequency_cutoff,
            "encoding_quality": self.encoding_quality,
            "quality_level": self.get_quality_level(),
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class ImageCompressionProfile:
    """Image compression profile"""
    profile_id: str
    name: str
    description: str
    
    # Algorithm settings
    algorithm: CompressionAlgorithm
    mode: CompressionMode
    target: CompressionTarget
    
    # Quality settings
    quality_level: int = 85         # 0-100 for lossy compression
    optimize_for_web: bool = True
    progressive_encoding: bool = True
    
    # Size settings
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    resize_algorithm: str = "lanczos"  # nearest, linear, cubic, lanczos
    
    # Format-specific settings
    # JPEG settings
    chroma_subsampling: str = "4:2:0"  # 4:4:4, 4:2:2, 4:2:0
    optimize_huffman: bool = True
    
    # WebP settings
    lossless_webp: bool = False
    webp_method: int = 6            # 0-6, higher = better compression
    
    # PNG settings
    png_compression_level: int = 6   # 0-9
    png_strategy: str = "default"    # default, filtered, huffman_only, rle, fixed
    
    # AVIF settings
    avif_speed: int = 6             # 0-10, higher = faster
    avif_effort: int = 4            # 0-9, higher = better compression
    
    # Color settings
    color_profile: str = "sRGB"     # sRGB, Adobe RGB, ProPhoto RGB
    preserve_color_profile: bool = False
    
    # Metadata
    strip_metadata: bool = True     # Remove EXIF/metadata
    preserve_copyright: bool = True
    
    # Performance
    parallel_processing: bool = True
    
    # Output
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def calculate_compression_ratio(self, original_size: int, 
                                  compressed_size: int) -> float:
        """Calculate compression ratio"""
        if compressed_size > 0:
            return original_size / compressed_size
        return 0.0
    
    def estimate_compressed_size(self, original_width: int, original_height: int, 
                               bytes_per_pixel: int = 3) -> int:
        """Estimate compressed size in bytes"""
        # Calculate target dimensions
        target_width = min(original_width, self.max_width or original_width)
        target_height = min(original_height, self.max_height or original_height)
        
        # Maintain aspect ratio if requested
        if self.maintain_aspect_ratio and (self.max_width or self.max_height):
            aspect_ratio = original_width / original_height
            
            if self.max_width and self.max_height:
                if target_width / target_height > aspect_ratio:
                    target_width = int(target_height * aspect_ratio)
                else:
                    target_height = int(target_width / aspect_ratio)
            elif self.max_width:
                target_height = int(target_width / aspect_ratio)
            elif self.max_height:
                target_width = int(target_height * aspect_ratio)
        
        # Calculate raw size
        raw_size = target_width * target_height * bytes_per_pixel
        
        # Estimate compression based on algorithm and quality
        if self.algorithm == CompressionAlgorithm.JPEG:
            compression_factor = (100 - self.quality_level) / 100 * 0.9 + 0.1
        elif self.algorithm == CompressionAlgorithm.WEBP:
            compression_factor = (100 - self.quality_level) / 100 * 0.8 + 0.1
        elif self.algorithm == CompressionAlgorithm.AVIF:
            compression_factor = (100 - self.quality_level) / 100 * 0.7 + 0.1
        elif self.algorithm == CompressionAlgorithm.PNG:
            compression_factor = 0.7  # PNG is lossless but still compresses
        else:
            compression_factor = 0.5  # Default estimate
        
        return int(raw_size * compression_factor)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "algorithm": self.algorithm.value,
            "mode": self.mode.value,
            "target": self.target.value,
            "quality_level": self.quality_level,
            "optimize_for_web": self.optimize_for_web,
            "progressive_encoding": self.progressive_encoding,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "maintain_aspect_ratio": self.maintain_aspect_ratio,
            "resize_algorithm": self.resize_algorithm,
            "chroma_subsampling": self.chroma_subsampling,
            "optimize_huffman": self.optimize_huffman,
            "lossless_webp": self.lossless_webp,
            "webp_method": self.webp_method,
            "png_compression_level": self.png_compression_level,
            "png_strategy": self.png_strategy,
            "avif_speed": self.avif_speed,
            "avif_effort": self.avif_effort,
            "color_profile": self.color_profile,
            "preserve_color_profile": self.preserve_color_profile,
            "strip_metadata": self.strip_metadata,
            "preserve_copyright": self.preserve_copyright,
            "parallel_processing": self.parallel_processing,
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class CompressionJob:
    """Compression job"""
    job_id: str
    user_id: str
    input_file_path: str
    output_file_path: str
    
    # Job configuration
    media_type: str                 # video, audio, image
    profile_id: str                 # Compression profile to use
    
    # Job metadata
    title: str = ""
    description: str = ""
    priority: int = 5
    
    # Job status
    status: str = "pending"         # pending, processing, completed, failed
    progress_percentage: float = 0.0
    
    # Timing
    created_date: datetime = field(default_factory=datetime.now)
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # File information
    input_file_size_bytes: int = 0
    output_file_size_bytes: int = 0
    compression_ratio: float = 0.0
    
    # Quality metrics
    quality_score: Optional[float] = None
    psnr_db: Optional[float] = None
    ssim_score: Optional[float] = None
    
    # Processing information
    processing_time_seconds: float = 0.0
    worker_id: str = ""
    error_message: str = ""
    
    def calculate_savings(self) -> Dict[str, Any]:
        """Calculate compression savings"""
        if self.input_file_size_bytes > 0 and self.output_file_size_bytes > 0:
            saved_bytes = self.input_file_size_bytes - self.output_file_size_bytes
            saved_percentage = (saved_bytes / self.input_file_size_bytes) * 100
            
            return {
                "saved_bytes": saved_bytes,
                "saved_mb": saved_bytes / (1024 * 1024),
                "saved_percentage": saved_percentage,
                "compression_ratio": self.compression_ratio
            }
        
        return {
            "saved_bytes": 0,
            "saved_mb": 0.0,
            "saved_percentage": 0.0,
            "compression_ratio": 0.0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        duration = timedelta(0)
        if self.started_date and self.completed_date:
            duration = self.completed_date - self.started_date
        
        savings = self.calculate_savings()
        
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "input_file_path": self.input_file_path,
            "output_file_path": self.output_file_path,
            "media_type": self.media_type,
            "profile_id": self.profile_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "created_date": self.created_date.isoformat(),
            "started_date": self.started_date.isoformat() if self.started_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "duration_seconds": int(duration.total_seconds()),
            "input_file_size_bytes": self.input_file_size_bytes,
            "output_file_size_bytes": self.output_file_size_bytes,
            "compression_ratio": self.compression_ratio,
            "quality_score": self.quality_score,
            "psnr_db": self.psnr_db,
            "ssim_score": self.ssim_score,
            "processing_time_seconds": self.processing_time_seconds,
            "worker_id": self.worker_id,
            "error_message": self.error_message,
            "savings": savings
        }

class CompressionConfiguration:
    """Main compression configuration manager"""
    
    def __init__(self) -> None:
        """Initialize compression configuration"""
        # Data storage
        self.video_profiles: Dict[str, VideoCompressionProfile] = {}
        self.audio_profiles: Dict[str, AudioCompressionProfile] = {}
        self.image_profiles: Dict[str, ImageCompressionProfile] = {}
        self.jobs: Dict[str, CompressionJob] = {}
        
        # Global settings
        self.compression_enabled = True
        self.hardware_acceleration = True
        self.parallel_processing = True
        self.quality_analysis = True
        
        # Performance settings
        self.performance_settings = {
            "max_concurrent_jobs": 8,
            "max_memory_usage_gb": 16,
            "max_cpu_usage_percent": 80,
            "temp_directory": "/tmp/compression",
            "cleanup_temp_files": True,
            "job_timeout_hours": 24,
            "retry_attempts": 3,
            "progress_update_interval": 10
        }
        
        # Quality settings
        self.quality_settings = {
            "default_quality_metric": "ssim",
            "quality_threshold": 0.95,
            "automatic_quality_adjustment": True,
            "preserve_original_quality": True,
            "content_adaptive_compression": True,
            "perceptual_optimization": True
        }
        
        # Output settings
        self.output_settings = {
            "preserve_timestamps": True,
            "preserve_permissions": True,
            "backup_original": False,
            "output_naming_pattern": "{name}_compressed.{ext}",
            "create_comparison_images": False,
            "generate_quality_report": True
        }
        
        # Initialize default profiles
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self) -> None:
        """Initialize default compression profiles"""
        
        # Video compression profiles
        video_profiles = [
            # Web streaming optimized
            VideoCompressionProfile(
                profile_id="web_streaming_hd",
                name="Web Streaming HD",
                description="Optimized for HD web streaming",
                algorithm=CompressionAlgorithm.H264,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.FAST,
                target=CompressionTarget.WEB_STREAMING,
                quality_settings=CompressionQualitySettings(
                    target_quality=85.0,
                    min_quality=70.0,
                    max_quality=95.0,
                    quality_metric=QualityMetric.SSIM,
                    target_bitrate_kbps=2500,
                    max_bitrate_kbps=3500,
                    variable_bitrate=True
                ),
                resolution_width=1280,
                resolution_height=720,
                target_fps=30.0
            ),
            
            # Mobile optimized
            VideoCompressionProfile(
                profile_id="mobile_optimized",
                name="Mobile Optimized",
                description="Optimized for mobile devices",
                algorithm=CompressionAlgorithm.H264,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.FAST,
                target=CompressionTarget.MOBILE_STREAMING,
                quality_settings=CompressionQualitySettings(
                    target_quality=75.0,
                    min_quality=60.0,
                    max_quality=85.0,
                    quality_metric=QualityMetric.VMAF,
                    target_bitrate_kbps=800,
                    max_bitrate_kbps=1200,
                    variable_bitrate=True
                ),
                resolution_width=854,
                resolution_height=480,
                target_fps=30.0
            ),
            
            # High efficiency (HEVC)
            VideoCompressionProfile(
                profile_id="hevc_high_efficiency",
                name="HEVC High Efficiency",
                description="High efficiency video codec",
                algorithm=CompressionAlgorithm.H265,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.MEDIUM,
                target=CompressionTarget.ARCHIVE,
                quality_settings=CompressionQualitySettings(
                    target_quality=90.0,
                    min_quality=80.0,
                    max_quality=98.0,
                    quality_metric=QualityMetric.VMAF,
                    target_bitrate_kbps=3000,
                    max_bitrate_kbps=4000,
                    variable_bitrate=True,
                    two_pass_encoding=True
                ),
                resolution_width=1920,
                resolution_height=1080,
                target_fps=30.0,
                hardware_acceleration=True
            ),
            
            # Next-gen AV1
            VideoCompressionProfile(
                profile_id="av1_next_gen",
                name="AV1 Next Generation",
                description="Next-generation AV1 codec",
                algorithm=CompressionAlgorithm.AV1,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.SLOW,
                target=CompressionTarget.WEB_STREAMING,
                quality_settings=CompressionQualitySettings(
                    target_quality=88.0,
                    min_quality=75.0,
                    max_quality=95.0,
                    quality_metric=QualityMetric.VMAF,
                    target_bitrate_kbps=2000,
                    max_bitrate_kbps=2800,
                    variable_bitrate=True,
                    two_pass_encoding=True
                ),
                resolution_width=1920,
                resolution_height=1080,
                target_fps=30.0
            )
        ]
        
        for profile in video_profiles:
            self.video_profiles[profile.profile_id] = profile
        
        # Audio compression profiles
        audio_profiles = [
            # High quality AAC
            AudioCompressionProfile(
                profile_id="aac_high_quality",
                name="AAC High Quality",
                description="High quality AAC compression",
                algorithm=CompressionAlgorithm.AAC,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.MEDIUM,
                target=CompressionTarget.WEB_STREAMING,
                target_bitrate_kbps=192,
                sample_rate_hz=48000,
                channels=2,
                bit_depth=16,
                variable_bitrate=True,
                encoding_quality=7
            ),
            
            # Mobile optimized
            AudioCompressionProfile(
                profile_id="mobile_audio",
                name="Mobile Audio",
                description="Mobile optimized audio",
                algorithm=CompressionAlgorithm.AAC,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.FAST,
                target=CompressionTarget.MOBILE_STREAMING,
                target_bitrate_kbps=96,
                sample_rate_hz=44100,
                channels=2,
                bit_depth=16,
                variable_bitrate=True,
                encoding_quality=5
            ),
            
            # Lossless FLAC
            AudioCompressionProfile(
                profile_id="flac_lossless",
                name="FLAC Lossless",
                description="Lossless FLAC compression",
                algorithm=CompressionAlgorithm.FLAC,
                mode=CompressionMode.LOSSLESS,
                preset=CompressionPreset.MEDIUM,
                target=CompressionTarget.ARCHIVE,
                target_bitrate_kbps=1411,  # CD quality
                sample_rate_hz=44100,
                channels=2,
                bit_depth=16,
                variable_bitrate=False,
                encoding_quality=8
            ),
            
            # Podcast optimized
            AudioCompressionProfile(
                profile_id="podcast_optimized",
                name="Podcast Optimized",
                description="Optimized for podcast content",
                algorithm=CompressionAlgorithm.MP3,
                mode=CompressionMode.LOSSY,
                preset=CompressionPreset.FAST,
                target=CompressionTarget.DOWNLOAD,
                target_bitrate_kbps=96,
                sample_rate_hz=44100,
                channels=1,  # Mono
                bit_depth=16,
                variable_bitrate=True,
                normalize_audio=True,
                dynamic_range_compression=True,
                encoding_quality=6
            )
        ]
        
        for profile in audio_profiles:
            self.audio_profiles[profile.profile_id] = profile
        
        # Image compression profiles
        image_profiles = [
            # Web optimized JPEG
            ImageCompressionProfile(
                profile_id="web_jpeg",
                name="Web JPEG",
                description="Web optimized JPEG compression",
                algorithm=CompressionAlgorithm.JPEG,
                mode=CompressionMode.LOSSY,
                target=CompressionTarget.WEB_STREAMING,
                quality_level=85,
                optimize_for_web=True,
                progressive_encoding=True,
                max_width=1920,
                max_height=1080,
                chroma_subsampling="4:2:0",
                optimize_huffman=True,
                strip_metadata=True
            ),
            
            # Next-gen WebP
            ImageCompressionProfile(
                profile_id="webp_modern",
                name="WebP Modern",
                description="Modern WebP compression",
                algorithm=CompressionAlgorithm.WEBP,
                mode=CompressionMode.LOSSY,
                target=CompressionTarget.WEB_STREAMING,
                quality_level=80,
                optimize_for_web=True,
                max_width=1920,
                max_height=1080,
                lossless_webp=False,
                webp_method=6,
                strip_metadata=True
            ),
            
            # AVIF next-gen
            ImageCompressionProfile(
                profile_id="avif_next_gen",
                name="AVIF Next Generation",
                description="Next-generation AVIF compression",
                algorithm=CompressionAlgorithm.AVIF,
                mode=CompressionMode.LOSSY,
                target=CompressionTarget.WEB_STREAMING,
                quality_level=75,
                optimize_for_web=True,
                max_width=1920,
                max_height=1080,
                avif_speed=6,
                avif_effort=4,
                strip_metadata=True
            ),
            
            # Social media optimized
            ImageCompressionProfile(
                profile_id="social_media",
                name="Social Media",
                description="Optimized for social media platforms",
                algorithm=CompressionAlgorithm.JPEG,
                mode=CompressionMode.LOSSY,
                target=CompressionTarget.SOCIAL_MEDIA,
                quality_level=75,
                optimize_for_web=True,
                max_width=1080,
                max_height=1080,
                maintain_aspect_ratio=True,
                strip_metadata=True,
                optimize_huffman=True
            ),
            
            # Thumbnail generation
            ImageCompressionProfile(
                profile_id="thumbnail",
                name="Thumbnail",
                description="Small thumbnail images",
                algorithm=CompressionAlgorithm.JPEG,
                mode=CompressionMode.LOSSY,
                target=CompressionTarget.WEB_STREAMING,
                quality_level=70,
                optimize_for_web=True,
                max_width=300,
                max_height=300,
                maintain_aspect_ratio=True,
                strip_metadata=True
            )
        ]
        
        for profile in image_profiles:
            self.image_profiles[profile.profile_id] = profile
    
    def create_compression_job(self, job_data: Dict[str, Any]) -> CompressionJob:
        """Create compression job"""
        
        job = CompressionJob(
            job_id=job_data.get("job_id", f"compress_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            user_id=job_data["user_id"],
            input_file_path=job_data["input_file_path"],
            output_file_path=job_data["output_file_path"],
            media_type=job_data["media_type"],
            profile_id=job_data["profile_id"],
            title=job_data.get("title", ""),
            description=job_data.get("description", ""),
            priority=job_data.get("priority", 5)
        )
        
        self.jobs[job.job_id] = job
        return job
    
    async def start_compression_job(self, job_id: str) -> Dict[str, Any]:
        """Start compression job"""
        
        result = {
            "success": False,
            "job_id": job_id,
            "estimated_duration": None,
            "error": None
        }
        
        try:
            if job_id not in self.jobs:
                result["error"] = f"Job {job_id} not found"
                return result
            
            job = self.jobs[job_id]
            
            if job.status != "pending":
                result["error"] = f"Cannot start job in {job.status} state"
                return result
            
            # Update job status
            job.status = "processing"
            job.started_date = datetime.now()
            
            # Start compression process
            compression_result = await self._start_compression_process(job)
            
            if compression_result["success"]:
                result.update({
                    "success": True,
                    "estimated_duration": compression_result.get("estimated_duration")
                })
            else:
                job.status = "failed"
                job.error_message = compression_result.get("error", "Compression failed")
                result["error"] = job.error_message
        
        except Exception as e:
            if job_id in self.jobs:
                self.jobs[job_id].status = "failed"
                self.jobs[job_id].error_message = str(e)
            result["error"] = str(e)
        
        return result
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """Get compression statistics"""
        
        stats = {
            "total_jobs": len(self.jobs),
            "video_profiles": len(self.video_profiles),
            "audio_profiles": len(self.audio_profiles),
            "image_profiles": len(self.image_profiles),
            "jobs_by_status": {},
            "jobs_by_media_type": {},
            "total_bytes_saved": 0,
            "average_compression_ratio": 0.0,
            "total_processing_time_hours": 0.0
        }
        
        # Calculate statistics
        total_compression_ratios = []
        total_processing_seconds = 0
        total_bytes_saved = 0
        
        for job in self.jobs.values():
            # Count by status
            status = job.status
            stats["jobs_by_status"][status] = stats["jobs_by_status"].get(status, 0) + 1
            
            # Count by media type
            media_type = job.media_type
            stats["jobs_by_media_type"][media_type] = stats["jobs_by_media_type"].get(media_type, 0) + 1
            
            # Calculate savings and ratios
            if job.input_file_size_bytes > 0 and job.output_file_size_bytes > 0:
                saved_bytes = job.input_file_size_bytes - job.output_file_size_bytes
                total_bytes_saved += saved_bytes
                
                if job.compression_ratio > 0:
                    total_compression_ratios.append(job.compression_ratio)
            
            # Processing time
            total_processing_seconds += job.processing_time_seconds
        
        # Calculate averages
        if total_compression_ratios:
            stats["average_compression_ratio"] = sum(total_compression_ratios) / len(total_compression_ratios)
        
        stats["total_bytes_saved"] = total_bytes_saved
        stats["total_mb_saved"] = total_bytes_saved / (1024 * 1024)
        stats["total_processing_time_hours"] = total_processing_seconds / 3600
        
        return stats
    
    # Helper methods
    async def _start_compression_process(self, job: CompressionJob) -> Dict[str, Any]:
        """Start compression process"""
        # Simulate compression process
        return {
            "success": True,
            "estimated_duration": "5 minutes"
        }
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete compression configuration"""
        return {
            "compression_statistics": self.get_compression_statistics(),
            "video_profiles_count": len(self.video_profiles),
            "audio_profiles_count": len(self.audio_profiles),
            "image_profiles_count": len(self.image_profiles),
            "jobs_count": len(self.jobs),
            "global_settings": {
                "compression_enabled": self.compression_enabled,
                "hardware_acceleration": self.hardware_acceleration,
                "parallel_processing": self.parallel_processing,
                "quality_analysis": self.quality_analysis
            },
            "performance_settings": self.performance_settings,
            "quality_settings": self.quality_settings,
            "output_settings": self.output_settings
        }

# Global compression configuration instance
compression_config = CompressionConfiguration()

# Export main classes
__all__ = [
    "CompressionConfiguration",
    "CompressionAlgorithm",
    "CompressionMode",
    "CompressionPreset",
    "CompressionTarget",
    "QualityMetric",
    "CompressionQualitySettings",
    "VideoCompressionProfile",
    "AudioCompressionProfile",
    "ImageCompressionProfile",
    "CompressionJob",
    "compression_config"
]
