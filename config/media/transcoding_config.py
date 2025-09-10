#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Transcoding Configuration Module
==========================================

Enterprise-grade transcoding configuration for the Ainflue platform.
Comprehensive video and audio transcoding, format conversion, quality optimization,
hardware acceleration, and distributed processing features.

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
import asyncio

class TranscodingFormat(str, Enum):
    """Media formats"""
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"
    THREEGP = "3gp"
    
    # Audio formats
    MP3 = "mp3"
    AAC = "aac"
    WAV = "wav"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    
    # Streaming formats
    HLS = "hls"
    DASH = "dash"
    SMOOTH = "smooth"

class VideoCodec(str, Enum):
    """Video codecs"""
    H264 = "h264"            # AVC
    H265 = "h265"            # HEVC
    VP8 = "vp8"              # WebM
    VP9 = "vp9"              # WebM
    AV1 = "av1"              # Next-gen
    MPEG2 = "mpeg2"          # Legacy
    MPEG4 = "mpeg4"          # Legacy
    XVID = "xvid"            # DivX
    THEORA = "theora"        # Open source
    PRORES = "prores"        # Apple professional

class AudioCodec(str, Enum):
    """Audio codecs"""
    AAC = "aac"              # Advanced Audio Coding
    MP3 = "mp3"              # MPEG Layer-3
    OPUS = "opus"            # Low-latency
    VORBIS = "vorbis"        # Ogg Vorbis
    FLAC = "flac"            # Lossless
    PCM = "pcm"              # Uncompressed
    AC3 = "ac3"              # Dolby Digital
    DTS = "dts"              # Digital Theater System
    ALAC = "alac"            # Apple Lossless
    WMA = "wma"              # Windows Media Audio

class TranscodingPreset(str, Enum):
    """Transcoding presets"""
    ULTRA_FAST = "ultrafast"
    SUPER_FAST = "superfast"
    VERY_FAST = "veryfast"
    FASTER = "faster"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    SLOWER = "slower"
    VERY_SLOW = "veryslow"
    PLACEBO = "placebo"

class QualityProfile(str, Enum):
    """Quality profiles"""
    ULTRA_LOW = "ultra_low"      # 144p
    LOW = "low"                  # 240p
    STANDARD = "standard"        # 360p
    MEDIUM = "medium"            # 480p
    HIGH = "high"                # 720p
    FULL_HD = "full_hd"          # 1080p
    QUAD_HD = "quad_hd"          # 1440p
    ULTRA_HD = "ultra_hd"        # 4K (2160p)
    EIGHT_K = "eight_k"          # 8K (4320p)
    SOURCE = "source"            # Original quality

class TranscodingStatus(str, Enum):
    """Transcoding job status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class HardwareAcceleration(str, Enum):
    """Hardware acceleration types"""
    NONE = "none"
    NVIDIA_NVENC = "nvenc"       # NVIDIA GPU
    NVIDIA_NVDEC = "nvdec"       # NVIDIA GPU
    INTEL_QSV = "qsv"            # Intel Quick Sync
    AMD_VCE = "vce"              # AMD Video Coding Engine
    APPLE_VIDEOTOOLBOX = "videotoolbox"  # Apple VideoToolbox
    VAAPI = "vaapi"              # Video Acceleration API
    VDPAU = "vdpau"              # Video Decode and Presentation API

@dataclass
class VideoTranscodingProfile:
    """Video transcoding profile"""
    profile_id: str
    name: str
    description: str
    
    # Basic settings
    codec: VideoCodec
    container: TranscodingFormat
    preset: TranscodingPreset
    
    # Quality settings
    resolution: str               # e.g., "1920x1080"
    bitrate_kbps: int            # Target bitrate
    max_bitrate_kbps: int        # Maximum bitrate
    min_bitrate_kbps: int        # Minimum bitrate
    framerate: float             # Target framerate
    keyframe_interval: int       # GOP size
    
    # Advanced settings
    profile_level: str = "4.1"   # Codec profile level
    b_frames: int = 2            # B-frames count
    ref_frames: int = 3          # Reference frames
    crf: Optional[int] = None    # Constant Rate Factor (quality)
    two_pass: bool = False       # Two-pass encoding
    
    # Hardware acceleration
    hardware_accel: HardwareAcceleration = HardwareAcceleration.NONE
    
    # Filters and effects
    video_filters: List[str] = field(default_factory=list)
    denoise: bool = False
    deinterlace: bool = False
    upscale: bool = False
    
    # Metadata
    enabled: bool = True
    priority: int = 5            # 1-10, higher = more priority
    created_date: datetime = field(default_factory=datetime.now)
    
    def get_resolution_tuple(self) -> Tuple[int, int]:
        """Get resolution as tuple"""
        if 'x' in self.resolution:
            width, height = self.resolution.split('x')
            return (int(width), int(height))
        return (0, 0)
    
    def calculate_estimated_size_mb(self, duration_seconds: int) -> float:
        """Calculate estimated file size in MB"""
        # Rough estimation: bitrate * duration / 8 (convert to bytes) / 1024^2 (convert to MB)
        return (self.bitrate_kbps * duration_seconds) / (8 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "codec": self.codec.value,
            "container": self.container.value,
            "preset": self.preset.value,
            "resolution": self.resolution,
            "width": self.get_resolution_tuple()[0],
            "height": self.get_resolution_tuple()[1],
            "bitrate_kbps": self.bitrate_kbps,
            "max_bitrate_kbps": self.max_bitrate_kbps,
            "min_bitrate_kbps": self.min_bitrate_kbps,
            "framerate": self.framerate,
            "keyframe_interval": self.keyframe_interval,
            "profile_level": self.profile_level,
            "b_frames": self.b_frames,
            "ref_frames": self.ref_frames,
            "crf": self.crf,
            "two_pass": self.two_pass,
            "hardware_accel": self.hardware_accel.value,
            "video_filters": self.video_filters,
            "denoise": self.denoise,
            "deinterlace": self.deinterlace,
            "upscale": self.upscale,
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class AudioTranscodingProfile:
    """Audio transcoding profile"""
    profile_id: str
    name: str
    description: str
    
    # Basic settings
    codec: AudioCodec
    container: TranscodingFormat
    
    # Quality settings
    bitrate_kbps: int           # Target bitrate
    sample_rate_hz: int         # Sample rate (e.g., 44100, 48000)
    channels: int               # Audio channels (1=mono, 2=stereo, 6=5.1)
    bit_depth: int = 16         # Bit depth (16, 24, 32)
    
    # Advanced settings
    variable_bitrate: bool = False  # VBR vs CBR
    quality_factor: Optional[float] = None  # Quality factor for VBR
    
    # Audio processing
    audio_filters: List[str] = field(default_factory=list)
    normalize: bool = False
    noise_reduction: bool = False
    dynamic_range_compression: bool = False
    
    # Metadata
    enabled: bool = True
    priority: int = 5
    created_date: datetime = field(default_factory=datetime.now)
    
    def calculate_estimated_size_mb(self, duration_seconds: int) -> float:
        """Calculate estimated file size in MB"""
        return (self.bitrate_kbps * duration_seconds) / (8 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "codec": self.codec.value,
            "container": self.container.value,
            "bitrate_kbps": self.bitrate_kbps,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "variable_bitrate": self.variable_bitrate,
            "quality_factor": self.quality_factor,
            "audio_filters": self.audio_filters,
            "normalize": self.normalize,
            "noise_reduction": self.noise_reduction,
            "dynamic_range_compression": self.dynamic_range_compression,
            "enabled": self.enabled,
            "priority": self.priority,
            "created_date": self.created_date.isoformat()
        }

@dataclass
class TranscodingJob:
    """Transcoding job"""
    job_id: str
    user_id: str
    input_file_path: str
    output_directory: str
    
    # Job configuration
    video_profiles: List[str] = field(default_factory=list)  # Video profile IDs
    audio_profiles: List[str] = field(default_factory=list)  # Audio profile IDs
    output_formats: List[TranscodingFormat] = field(default_factory=list)
    
    # Job metadata
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    priority: int = 5            # 1-10, higher = more priority
    
    # Job status
    status: TranscodingStatus = TranscodingStatus.PENDING
    progress_percentage: float = 0.0
    current_task: str = ""
    estimated_completion: Optional[datetime] = None
    
    # Timing
    created_date: datetime = field(default_factory=datetime.now)
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # Input file information
    input_file_size_bytes: int = 0
    input_duration_seconds: float = 0.0
    input_video_codec: str = ""
    input_audio_codec: str = ""
    input_resolution: str = ""
    input_framerate: float = 0.0
    input_bitrate_kbps: int = 0
    
    # Output information
    output_files: List[Dict[str, Any]] = field(default_factory=list)
    total_output_size_bytes: int = 0
    
    # Processing information
    processing_node: str = ""
    worker_id: str = ""
    retry_count: int = 0
    max_retries: int = 3
    error_message: str = ""
    
    # Options
    delete_input_after_completion: bool = False
    generate_thumbnails: bool = True
    generate_previews: bool = True
    create_streaming_manifests: bool = True
    
    # Notifications
    notify_on_completion: bool = True
    notification_webhooks: List[str] = field(default_factory=list)
    notification_emails: List[str] = field(default_factory=list)
    
    def calculate_duration(self) -> timedelta:
        """Calculate job duration"""
        if self.started_date:
            end = self.completed_date or datetime.now()
            return end - self.started_date
        return timedelta(0)
    
    def calculate_eta(self) -> Optional[datetime]:
        """Calculate estimated completion time"""
        if self.progress_percentage > 0 and self.started_date:
            duration = datetime.now() - self.started_date
            total_estimated = duration / (self.progress_percentage / 100)
            return self.started_date + total_estimated
        return None
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio"""
        if self.input_file_size_bytes > 0 and self.total_output_size_bytes > 0:
            return self.input_file_size_bytes / self.total_output_size_bytes
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        duration = self.calculate_duration()
        eta = self.calculate_eta()
        
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "input_file_path": self.input_file_path,
            "output_directory": self.output_directory,
            "video_profiles": self.video_profiles,
            "audio_profiles": self.audio_profiles,
            "output_formats": [f.value for f in self.output_formats],
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "priority": self.priority,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "current_task": self.current_task,
            "estimated_completion": eta.isoformat() if eta else None,
            "created_date": self.created_date.isoformat(),
            "started_date": self.started_date.isoformat() if self.started_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "duration_seconds": int(duration.total_seconds()),
            "input_file_size_bytes": self.input_file_size_bytes,
            "input_duration_seconds": self.input_duration_seconds,
            "input_video_codec": self.input_video_codec,
            "input_audio_codec": self.input_audio_codec,
            "input_resolution": self.input_resolution,
            "input_framerate": self.input_framerate,
            "input_bitrate_kbps": self.input_bitrate_kbps,
            "output_files": self.output_files,
            "total_output_size_bytes": self.total_output_size_bytes,
            "compression_ratio": self.get_compression_ratio(),
            "processing_node": self.processing_node,
            "worker_id": self.worker_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "delete_input_after_completion": self.delete_input_after_completion,
            "generate_thumbnails": self.generate_thumbnails,
            "generate_previews": self.generate_previews,
            "create_streaming_manifests": self.create_streaming_manifests,
            "notify_on_completion": self.notify_on_completion,
            "notification_webhooks": self.notification_webhooks,
            "notification_emails": self.notification_emails
        }

@dataclass
class TranscodingPerformanceMetrics:
    """Transcoding performance metrics"""
    metric_id: str
    job_id: str
    timestamp: datetime
    
    # Performance metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    gpu_memory_usage_mb: float = 0.0
    
    # Throughput metrics
    frames_per_second: float = 0.0
    encoding_speed_multiplier: float = 0.0  # Real-time multiplier (1.0 = real-time)
    
    # Quality metrics
    psnr_db: Optional[float] = None         # Peak Signal-to-Noise Ratio
    ssim_score: Optional[float] = None      # Structural Similarity Index
    vmaf_score: Optional[float] = None      # Video Multimethod Assessment Fusion
    
    # Resource utilization
    io_read_mbps: float = 0.0
    io_write_mbps: float = 0.0
    network_upload_mbps: float = 0.0
    network_download_mbps: float = 0.0
    
    # Error tracking
    frame_drops: int = 0
    encoding_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_id": self.metric_id,
            "job_id": self.job_id,
            "timestamp": self.timestamp.isoformat(),
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "gpu_usage_percent": self.gpu_usage_percent,
            "gpu_memory_usage_mb": self.gpu_memory_usage_mb,
            "frames_per_second": self.frames_per_second,
            "encoding_speed_multiplier": self.encoding_speed_multiplier,
            "psnr_db": self.psnr_db,
            "ssim_score": self.ssim_score,
            "vmaf_score": self.vmaf_score,
            "io_read_mbps": self.io_read_mbps,
            "io_write_mbps": self.io_write_mbps,
            "network_upload_mbps": self.network_upload_mbps,
            "network_download_mbps": self.network_download_mbps,
            "frame_drops": self.frame_drops,
            "encoding_errors": self.encoding_errors
        }

@dataclass
class TranscodingClusterConfig:
    """Transcoding cluster configuration"""
    cluster_enabled: bool = True
    
    # Node configuration
    max_concurrent_jobs_per_node: int = 4
    max_total_jobs: int = 100
    load_balancing_strategy: str = "round_robin"  # round_robin, least_loaded, priority_based
    
    # Auto-scaling
    auto_scaling_enabled: bool = True
    min_nodes: int = 1
    max_nodes: int = 10
    scale_up_threshold: float = 0.8    # Scale up when 80% capacity
    scale_down_threshold: float = 0.3  # Scale down when 30% capacity
    scale_up_cooldown_minutes: int = 5
    scale_down_cooldown_minutes: int = 15
    
    # Health monitoring
    health_check_interval_seconds: int = 30
    node_timeout_seconds: int = 300
    job_timeout_hours: int = 12
    
    # Resource requirements
    default_cpu_cores: int = 4
    default_memory_gb: int = 8
    default_gpu_memory_gb: int = 4
    
    # Storage configuration
    shared_storage_enabled: bool = True
    storage_backend: str = "s3"        # s3, nfs, local
    input_storage_path: str = "/storage/input"
    output_storage_path: str = "/storage/output"
    temp_storage_path: str = "/storage/temp"
    
    # Network configuration
    internal_network: str = "10.0.0.0/16"
    communication_port: int = 8080
    secure_communication: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cluster_enabled": self.cluster_enabled,
            "max_concurrent_jobs_per_node": self.max_concurrent_jobs_per_node,
            "max_total_jobs": self.max_total_jobs,
            "load_balancing_strategy": self.load_balancing_strategy,
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "min_nodes": self.min_nodes,
            "max_nodes": self.max_nodes,
            "scale_up_threshold": self.scale_up_threshold,
            "scale_down_threshold": self.scale_down_threshold,
            "scale_up_cooldown_minutes": self.scale_up_cooldown_minutes,
            "scale_down_cooldown_minutes": self.scale_down_cooldown_minutes,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "node_timeout_seconds": self.node_timeout_seconds,
            "job_timeout_hours": self.job_timeout_hours,
            "default_cpu_cores": self.default_cpu_cores,
            "default_memory_gb": self.default_memory_gb,
            "default_gpu_memory_gb": self.default_gpu_memory_gb,
            "shared_storage_enabled": self.shared_storage_enabled,
            "storage_backend": self.storage_backend,
            "input_storage_path": self.input_storage_path,
            "output_storage_path": self.output_storage_path,
            "temp_storage_path": self.temp_storage_path,
            "internal_network": self.internal_network,
            "communication_port": self.communication_port,
            "secure_communication": self.secure_communication
        }

class TranscodingConfiguration:
    """Main transcoding configuration manager"""
    
    def __init__(self):
        """Initialize transcoding configuration"""
        # Configuration components
        self.cluster_config = TranscodingClusterConfig()
        
        # Data storage
        self.video_profiles: Dict[str, VideoTranscodingProfile] = {}
        self.audio_profiles: Dict[str, AudioTranscodingProfile] = {}
        self.jobs: Dict[str, TranscodingJob] = {}
        self.performance_metrics: List[TranscodingPerformanceMetrics] = []
        
        # Global settings
        self.transcoding_enabled = True
        self.hardware_acceleration_enabled = True
        self.distributed_processing = True
        self.quality_analysis_enabled = True
        
        # Performance settings
        self.performance_settings = {
            "max_concurrent_jobs": 10,
            "job_queue_size": 100,
            "worker_timeout_minutes": 60,
            "chunk_size_mb": 64,
            "memory_limit_gb": 16,
            "cpu_limit_cores": 8,
            "gpu_limit_count": 2,
            "temp_cleanup_enabled": True,
            "progress_update_interval_seconds": 5
        }
        
        # Quality settings
        self.quality_settings = {
            "automatic_quality_detection": True,
            "source_quality_preservation": True,
            "upscaling_enabled": True,
            "downscaling_enabled": True,
            "aspect_ratio_preservation": True,
            "keyframe_optimization": True,
            "bitrate_optimization": True,
            "quality_metrics_calculation": True
        }
        
        # Output settings
        self.output_settings = {
            "default_container": "mp4",
            "preserve_metadata": True,
            "generate_thumbnails": True,
            "thumbnail_count": 10,
            "generate_previews": True,
            "preview_duration_seconds": 30,
            "create_manifest_files": True,
            "segment_hls": True,
            "segment_dash": True
        }
        
        # Notification settings
        self.notification_settings = {
            "webhook_notifications": True,
            "email_notifications": True,
            "slack_notifications": False,
            "discord_notifications": False,
            "completion_notifications": True,
            "error_notifications": True,
            "progress_notifications": False,
            "batch_notifications": True
        }
        
        # Analytics settings
        self.analytics_settings = {
            "performance_tracking": True,
            "resource_monitoring": True,
            "quality_analysis": True,
            "cost_tracking": True,
            "usage_statistics": True,
            "trend_analysis": True,
            "reporting_enabled": True,
            "real_time_dashboard": True
        }
        
        # Initialize default profiles
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self):
        """Initialize default transcoding profiles"""
        
        # Default video profiles
        video_profiles = [
            # Mobile optimized
            VideoTranscodingProfile(
                profile_id="mobile_240p",
                name="Mobile 240p",
                description="Ultra-low quality for mobile data saving",
                codec=VideoCodec.H264,
                container=TranscodingFormat.MP4,
                preset=TranscodingPreset.FAST,
                resolution="426x240",
                bitrate_kbps=400,
                max_bitrate_kbps=600,
                min_bitrate_kbps=200,
                framerate=15.0,
                keyframe_interval=30,
                profile_level="3.0",
                crf=28,
                priority=3
            ),
            
            # Standard quality
            VideoTranscodingProfile(
                profile_id="standard_480p",
                name="Standard 480p",
                description="Standard quality for web streaming",
                codec=VideoCodec.H264,
                container=TranscodingFormat.MP4,
                preset=TranscodingPreset.MEDIUM,
                resolution="854x480",
                bitrate_kbps=1200,
                max_bitrate_kbps=1800,
                min_bitrate_kbps=800,
                framerate=30.0,
                keyframe_interval=60,
                profile_level="3.1",
                crf=23,
                priority=5
            ),
            
            # HD quality
            VideoTranscodingProfile(
                profile_id="hd_720p",
                name="HD 720p",
                description="High definition quality",
                codec=VideoCodec.H264,
                container=TranscodingFormat.MP4,
                preset=TranscodingPreset.MEDIUM,
                resolution="1280x720",
                bitrate_kbps=2500,
                max_bitrate_kbps=3500,
                min_bitrate_kbps=1500,
                framerate=30.0,
                keyframe_interval=60,
                profile_level="4.0",
                crf=20,
                priority=7
            ),
            
            # Full HD quality
            VideoTranscodingProfile(
                profile_id="fullhd_1080p",
                name="Full HD 1080p",
                description="Full high definition quality",
                codec=VideoCodec.H264,
                container=TranscodingFormat.MP4,
                preset=TranscodingPreset.MEDIUM,
                resolution="1920x1080",
                bitrate_kbps=4500,
                max_bitrate_kbps=6000,
                min_bitrate_kbps=3000,
                framerate=30.0,
                keyframe_interval=60,
                profile_level="4.1",
                crf=18,
                priority=8
            ),
            
            # 4K quality
            VideoTranscodingProfile(
                profile_id="4k_2160p",
                name="4K Ultra HD",
                description="Ultra high definition 4K quality",
                codec=VideoCodec.H265,
                container=TranscodingFormat.MP4,
                preset=TranscodingPreset.SLOW,
                resolution="3840x2160",
                bitrate_kbps=15000,
                max_bitrate_kbps=20000,
                min_bitrate_kbps=10000,
                framerate=30.0,
                keyframe_interval=60,
                profile_level="5.1",
                crf=16,
                hardware_accel=HardwareAcceleration.NVIDIA_NVENC,
                priority=9
            ),
            
            # WebM optimized
            VideoTranscodingProfile(
                profile_id="webm_720p",
                name="WebM 720p",
                description="WebM format for web optimization",
                codec=VideoCodec.VP9,
                container=TranscodingFormat.WEBM,
                preset=TranscodingPreset.MEDIUM,
                resolution="1280x720",
                bitrate_kbps=2000,
                max_bitrate_kbps=2800,
                min_bitrate_kbps=1200,
                framerate=30.0,
                keyframe_interval=120,
                crf=32,
                two_pass=True,
                priority=6
            )
        ]
        
        # Store video profiles
        for profile in video_profiles:
            self.video_profiles[profile.profile_id] = profile
        
        # Default audio profiles
        audio_profiles = [
            # Low quality
            AudioTranscodingProfile(
                profile_id="audio_low",
                name="Low Quality Audio",
                description="Low quality audio for data saving",
                codec=AudioCodec.AAC,
                container=TranscodingFormat.MP4,
                bitrate_kbps=64,
                sample_rate_hz=22050,
                channels=2,
                bit_depth=16,
                priority=3
            ),
            
            # Standard quality
            AudioTranscodingProfile(
                profile_id="audio_standard",
                name="Standard Quality Audio",
                description="Standard quality audio",
                codec=AudioCodec.AAC,
                container=TranscodingFormat.MP4,
                bitrate_kbps=128,
                sample_rate_hz=44100,
                channels=2,
                bit_depth=16,
                priority=5
            ),
            
            # High quality
            AudioTranscodingProfile(
                profile_id="audio_high",
                name="High Quality Audio",
                description="High quality audio",
                codec=AudioCodec.AAC,
                container=TranscodingFormat.MP4,
                bitrate_kbps=192,
                sample_rate_hz=48000,
                channels=2,
                bit_depth=16,
                priority=7
            ),
            
            # Lossless
            AudioTranscodingProfile(
                profile_id="audio_lossless",
                name="Lossless Audio",
                description="Lossless audio quality",
                codec=AudioCodec.FLAC,
                container=TranscodingFormat.FLAC,
                bitrate_kbps=1411,  # CD quality
                sample_rate_hz=44100,
                channels=2,
                bit_depth=16,
                priority=9
            ),
            
            # Podcast optimized
            AudioTranscodingProfile(
                profile_id="audio_podcast",
                name="Podcast Audio",
                description="Optimized for podcast/voice content",
                codec=AudioCodec.MP3,
                container=TranscodingFormat.MP3,
                bitrate_kbps=96,
                sample_rate_hz=44100,
                channels=1,  # Mono
                bit_depth=16,
                normalize=True,
                noise_reduction=True,
                dynamic_range_compression=True,
                priority=6
            )
        ]
        
        # Store audio profiles
        for profile in audio_profiles:
            self.audio_profiles[profile.profile_id] = profile
    
    def create_transcoding_job(self, job_data: Dict[str, Any]) -> TranscodingJob:
        """Create transcoding job"""
        
        job = TranscodingJob(
            job_id=job_data.get("job_id", f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            user_id=job_data["user_id"],
            input_file_path=job_data["input_file_path"],
            output_directory=job_data.get("output_directory", "/storage/output"),
            video_profiles=job_data.get("video_profiles", ["standard_480p"]),
            audio_profiles=job_data.get("audio_profiles", ["audio_standard"]),
            output_formats=[TranscodingFormat(f) for f in job_data.get("output_formats", ["mp4"])],
            title=job_data.get("title", ""),
            description=job_data.get("description", ""),
            tags=job_data.get("tags", []),
            priority=job_data.get("priority", 5),
            delete_input_after_completion=job_data.get("delete_input_after_completion", False),
            generate_thumbnails=job_data.get("generate_thumbnails", True),
            generate_previews=job_data.get("generate_previews", True),
            create_streaming_manifests=job_data.get("create_streaming_manifests", True),
            notify_on_completion=job_data.get("notify_on_completion", True),
            notification_webhooks=job_data.get("notification_webhooks", []),
            notification_emails=job_data.get("notification_emails", [])
        )
        
        self.jobs[job.job_id] = job
        return job
    
    async def start_transcoding_job(self, job_id: str) -> Dict[str, Any]:
        """Start transcoding job"""
        
        start_result = {
            "success": False,
            "job_id": job_id,
            "estimated_completion": None,
            "error": None
        }
        
        try:
            if job_id not in self.jobs:
                start_result["error"] = f"Job {job_id} not found"
                return start_result
            
            job = self.jobs[job_id]
            
            # Check if job can be started
            if job.status != TranscodingStatus.PENDING:
                start_result["error"] = f"Cannot start job in {job.status.value} state"
                return start_result
            
            # Update job status
            job.status = TranscodingStatus.QUEUED
            job.started_date = datetime.now()
            
            # Estimate completion time
            estimated_duration = self._estimate_transcoding_duration(job)
            job.estimated_completion = job.started_date + estimated_duration
            
            # Start transcoding process
            processing_result = await self._start_transcoding_process(job)
            
            if processing_result["success"]:
                job.status = TranscodingStatus.PROCESSING
                job.processing_node = processing_result.get("processing_node", "")
                job.worker_id = processing_result.get("worker_id", "")
                
                start_result.update({
                    "success": True,
                    "estimated_completion": job.estimated_completion.isoformat() if job.estimated_completion else None
                })
            else:
                job.status = TranscodingStatus.FAILED
                job.error_message = processing_result.get("error", "Failed to start processing")
                start_result["error"] = job.error_message
        
        except Exception as e:
            if job_id in self.jobs:
                self.jobs[job_id].status = TranscodingStatus.FAILED
                self.jobs[job_id].error_message = str(e)
            start_result["error"] = str(e)
        
        return start_result
    
    async def cancel_transcoding_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel transcoding job"""
        
        cancel_result = {
            "success": False,
            "job_id": job_id,
            "error": None
        }
        
        try:
            if job_id not in self.jobs:
                cancel_result["error"] = f"Job {job_id} not found"
                return cancel_result
            
            job = self.jobs[job_id]
            
            if job.status in [TranscodingStatus.COMPLETED, TranscodingStatus.FAILED, TranscodingStatus.CANCELLED]:
                cancel_result["error"] = f"Cannot cancel job in {job.status.value} state"
                return cancel_result
            
            # Cancel the job
            cancellation_result = await self._cancel_transcoding_process(job)
            
            if cancellation_result["success"]:
                job.status = TranscodingStatus.CANCELLED
                job.completed_date = datetime.now()
                cancel_result["success"] = True
            else:
                cancel_result["error"] = cancellation_result.get("error", "Failed to cancel job")
        
        except Exception as e:
            cancel_result["error"] = str(e)
        
        return cancel_result
    
    def update_job_progress(self, job_id: str, progress_data: Dict[str, Any]) -> None:
        """Update job progress"""
        
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        
        # Update progress
        if "progress_percentage" in progress_data:
            job.progress_percentage = progress_data["progress_percentage"]
        
        if "current_task" in progress_data:
            job.current_task = progress_data["current_task"]
        
        # Update file information
        if "input_file_size_bytes" in progress_data:
            job.input_file_size_bytes = progress_data["input_file_size_bytes"]
        
        if "input_duration_seconds" in progress_data:
            job.input_duration_seconds = progress_data["input_duration_seconds"]
        
        if "output_files" in progress_data:
            job.output_files = progress_data["output_files"]
            job.total_output_size_bytes = sum(f.get("size_bytes", 0) for f in job.output_files)
        
        # Update estimated completion
        if job.progress_percentage > 0:
            job.estimated_completion = job.calculate_eta()
        
        # Store performance metrics if provided
        if "performance_metrics" in progress_data:
            metrics = TranscodingPerformanceMetrics(
                metric_id=f"metric_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                job_id=job_id,
                timestamp=datetime.now(),
                **progress_data["performance_metrics"]
            )
            self.performance_metrics.append(metrics)
            
            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.performance_metrics = [
                m for m in self.performance_metrics
                if m.timestamp > cutoff_time
            ]
    
    def get_job_queue(self, status_filter: Optional[TranscodingStatus] = None) -> List[Dict[str, Any]]:
        """Get job queue"""
        
        jobs = []
        
        for job in self.jobs.values():
            if status_filter is None or job.status == status_filter:
                jobs.append(job.to_dict())
        
        # Sort by priority (descending) and creation date (ascending)
        jobs.sort(key=lambda x: (-x["priority"], x["created_date"]))
        
        return jobs
    
    def get_transcoding_statistics(self) -> Dict[str, Any]:
        """Get transcoding statistics"""
        
        stats = {
            "total_jobs": len(self.jobs),
            "video_profiles": len(self.video_profiles),
            "audio_profiles": len(self.audio_profiles),
            "performance_metrics": len(self.performance_metrics),
            "jobs_by_status": {},
            "jobs_by_format": {},
            "average_compression_ratio": 0.0,
            "total_processing_time_hours": 0.0,
            "total_input_size_gb": 0.0,
            "total_output_size_gb": 0.0
        }
        
        # Calculate statistics
        total_compression_ratios = []
        total_processing_seconds = 0
        total_input_bytes = 0
        total_output_bytes = 0
        
        for job in self.jobs.values():
            # Count by status
            status = job.status.value
            stats["jobs_by_status"][status] = stats["jobs_by_status"].get(status, 0) + 1
            
            # Count by format
            for format_enum in job.output_formats:
                format_str = format_enum.value
                stats["jobs_by_format"][format_str] = stats["jobs_by_format"].get(format_str, 0) + 1
            
            # Calculate totals
            if job.input_file_size_bytes > 0:
                total_input_bytes += job.input_file_size_bytes
            
            if job.total_output_size_bytes > 0:
                total_output_bytes += job.total_output_size_bytes
            
            compression_ratio = job.get_compression_ratio()
            if compression_ratio > 0:
                total_compression_ratios.append(compression_ratio)
            
            if job.status in [TranscodingStatus.COMPLETED, TranscodingStatus.FAILED]:
                duration = job.calculate_duration()
                total_processing_seconds += duration.total_seconds()
        
        # Calculate averages
        if total_compression_ratios:
            stats["average_compression_ratio"] = sum(total_compression_ratios) / len(total_compression_ratios)
        
        stats["total_processing_time_hours"] = total_processing_seconds / 3600
        stats["total_input_size_gb"] = total_input_bytes / (1024 ** 3)
        stats["total_output_size_gb"] = total_output_bytes / (1024 ** 3)
        
        return stats
    
    def get_performance_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance analytics"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.performance_metrics
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "time_period_hours": hours,
                "data_points": 0,
                "metrics": {}
            }
        
        # Calculate aggregated metrics
        total_metrics = len(recent_metrics)
        
        analytics = {
            "time_period_hours": hours,
            "data_points": total_metrics,
            "metrics": {
                "average_cpu_usage_percent": sum(m.cpu_usage_percent for m in recent_metrics) / total_metrics,
                "average_memory_usage_mb": sum(m.memory_usage_mb for m in recent_metrics) / total_metrics,
                "average_gpu_usage_percent": sum(m.gpu_usage_percent for m in recent_metrics) / total_metrics,
                "average_encoding_speed": sum(m.encoding_speed_multiplier for m in recent_metrics) / total_metrics,
                "average_fps": sum(m.frames_per_second for m in recent_metrics) / total_metrics,
                "total_frame_drops": sum(m.frame_drops for m in recent_metrics),
                "total_encoding_errors": sum(m.encoding_errors for m in recent_metrics)
            },
            "quality_metrics": {
                "average_psnr_db": None,
                "average_ssim_score": None,
                "average_vmaf_score": None
            }
        }
        
        # Calculate quality metrics if available
        psnr_values = [m.psnr_db for m in recent_metrics if m.psnr_db is not None]
        ssim_values = [m.ssim_score for m in recent_metrics if m.ssim_score is not None]
        vmaf_values = [m.vmaf_score for m in recent_metrics if m.vmaf_score is not None]
        
        if psnr_values:
            analytics["quality_metrics"]["average_psnr_db"] = sum(psnr_values) / len(psnr_values)
        
        if ssim_values:
            analytics["quality_metrics"]["average_ssim_score"] = sum(ssim_values) / len(ssim_values)
        
        if vmaf_values:
            analytics["quality_metrics"]["average_vmaf_score"] = sum(vmaf_values) / len(vmaf_values)
        
        return analytics
    
    def search_jobs(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search transcoding jobs"""
        
        matching_jobs = []
        
        for job in self.jobs.values():
            if self._matches_job_criteria(job, search_criteria):
                matching_jobs.append(job.to_dict())
        
        # Sort by creation date (descending)
        matching_jobs.sort(key=lambda x: x["created_date"], reverse=True)
        
        return matching_jobs
    
    # Helper methods
    def _estimate_transcoding_duration(self, job: TranscodingJob) -> timedelta:
        """Estimate transcoding duration"""
        # Simple estimation based on input duration and number of profiles
        base_duration = job.input_duration_seconds or 300  # Default 5 minutes
        profile_count = len(job.video_profiles) + len(job.audio_profiles)
        estimated_seconds = base_duration * profile_count * 0.5  # Assume 0.5x real-time
        return timedelta(seconds=estimated_seconds)
    
    async def _start_transcoding_process(self, job: TranscodingJob) -> Dict[str, Any]:
        """Start transcoding process"""
        # Simulate starting transcoding process
        return {
            "success": True,
            "processing_node": "transcode-node-01",
            "worker_id": f"worker_{datetime.now().strftime('%H%M%S')}"
        }
    
    async def _cancel_transcoding_process(self, job: TranscodingJob) -> Dict[str, Any]:
        """Cancel transcoding process"""
        # Simulate cancelling transcoding process
        return {"success": True}
    
    def _matches_job_criteria(self, job: TranscodingJob, criteria: Dict[str, Any]) -> bool:
        """Check if job matches search criteria"""
        # Simple implementation - check title and tags
        search_term = criteria.get("search_term", "").lower()
        
        if search_term:
            if search_term not in job.title.lower():
                if not any(search_term in tag.lower() for tag in job.tags):
                    return False
        
        # Check status
        if "status" in criteria and criteria["status"] != job.status.value:
            return False
        
        # Check user
        if "user_id" in criteria and criteria["user_id"] != job.user_id:
            return False
        
        # Check date range
        if "start_date" in criteria:
            start_date = datetime.fromisoformat(criteria["start_date"])
            if job.created_date < start_date:
                return False
        
        if "end_date" in criteria:
            end_date = datetime.fromisoformat(criteria["end_date"])
            if job.created_date > end_date:
                return False
        
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete transcoding configuration"""
        return {
            "transcoding_statistics": self.get_transcoding_statistics(),
            "performance_analytics": self.get_performance_analytics(),
            "cluster_config": self.cluster_config.to_dict(),
            "video_profiles_count": len(self.video_profiles),
            "audio_profiles_count": len(self.audio_profiles),
            "jobs_count": len(self.jobs),
            "metrics_count": len(self.performance_metrics),
            "global_settings": {
                "transcoding_enabled": self.transcoding_enabled,
                "hardware_acceleration_enabled": self.hardware_acceleration_enabled,
                "distributed_processing": self.distributed_processing,
                "quality_analysis_enabled": self.quality_analysis_enabled
            },
            "performance_settings": self.performance_settings,
            "quality_settings": self.quality_settings,
            "output_settings": self.output_settings,
            "notification_settings": self.notification_settings,
            "analytics_settings": self.analytics_settings
        }

# Global transcoding configuration instance
transcoding_config = TranscodingConfiguration()

# Export main classes
__all__ = [
    "TranscodingConfiguration",
    "TranscodingFormat",
    "VideoCodec",
    "AudioCodec",
    "TranscodingPreset",
    "QualityProfile",
    "TranscodingStatus",
    "HardwareAcceleration",
    "VideoTranscodingProfile",
    "AudioTranscodingProfile",
    "TranscodingJob",
    "TranscodingPerformanceMetrics",
    "TranscodingClusterConfig",
    "transcoding_config"
]
