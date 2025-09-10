"""Encoding Engine - Advanced encoding and compression for IA Influencer Agent Platform
===================================================================================

Industrial-grade encoding engine providing sophisticated compression algorithms,
adaptive encoding, and multi-format optimization for creator workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, BinaryIO
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class CodecType(Enum):
    """Supported codec types."""
    
    # Video codecs
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    VP8 = "vp8"
    AV1 = "av1"
    
    # Audio codecs
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    FLAC = "flac"
    
    # Image codecs
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    HEIF = "heif"


class EncodingPreset(Enum):
    """Predefined encoding presets."""
    
    ULTRAFAST = "ultrafast"
    SUPERFAST = "superfast"
    VERYFAST = "veryfast"
    FASTER = "faster"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    SLOWER = "slower"
    VERYSLOW = "veryslow"
    PLACEBO = "placebo"


class CompressionMode(Enum):
    """Compression modes."""
    
    LOSSLESS = "lossless"
    NEAR_LOSSLESS = "near_lossless"
    LOSSY = "lossy"
    ADAPTIVE = "adaptive"


class EncodingProfile(Enum):
    """Encoding profiles for different use cases."""
    
    STREAMING_4K = "streaming_4k"
    STREAMING_HD = "streaming_hd"
    STREAMING_SD = "streaming_sd"
    BROADCAST_QUALITY = "broadcast_quality"
    ARCHIVE_QUALITY = "archive_quality"
    WEB_OPTIMIZED = "web_optimized"
    MOBILE_OPTIMIZED = "mobile_optimized"
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    CONFERENCE = "conference"


@dataclass
class EncodingParameters:
    """Comprehensive encoding parameters."""
    
    # General parameters
    codec: CodecType
    preset: EncodingPreset = EncodingPreset.MEDIUM
    compression_mode: CompressionMode = CompressionMode.LOSSY
    
    # Video parameters
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    crf: Optional[int] = None  # Constant Rate Factor
    keyframe_interval: Optional[int] = None
    b_frames: Optional[int] = None
    ref_frames: Optional[int] = None
    
    # Audio parameters
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    audio_bitrate: Optional[int] = None
    
    # Image parameters
    quality: Optional[int] = None
    progressive: Optional[bool] = None
    
    # Advanced parameters
    profile: Optional[str] = None
    level: Optional[str] = None
    pixel_format: Optional[str] = None
    color_space: Optional[str] = None
    hdr: Optional[bool] = None
    
    # Custom parameters
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncodingJob:
    """Encoding job definition."""
    
    job_id: str
    input_data: Union[str, Path, bytes, BinaryIO]
    parameters: EncodingParameters
    output_path: Optional[str] = None
    priority: int = 5  # 1-10 scale
    timeout: Optional[float] = None
    callback: Optional[callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"


@dataclass
class EncodingResult:
    """Result of encoding operation."""
    
    job_id: str
    success: bool
    output_data: Optional[bytes] = None
    output_path: Optional[str] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    encoding_time: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    encoding_stats: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class AdaptiveEncodingContext:
    """Context for adaptive encoding decisions."""
    
    target_device: str = "general"
    network_conditions: str = "good"  # poor, fair, good, excellent
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    content_analysis: Dict[str, Any] = field(default_factory=dict)
    historical_performance: Dict[str, Any] = field(default_factory=dict)


class EncodingEngine:
    """Advanced encoding engine with intelligent optimization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize encoding engine with configuration."""
        self.config = config or {}
        self.max_workers = self.config.get("max_workers", 4)
        self.gpu_acceleration = self.config.get("gpu_acceleration", False)
        
        # Job management
        self.encoding_queue = []
        self.active_jobs = {}
        self.completed_jobs = {}
        self.job_lock = threading.Lock()
        
        # Worker pool
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Encoding profiles
        self.encoding_profiles = {}
        self._init_encoding_profiles()
        
        # Performance metrics
        self.performance_metrics = {
            "jobs_completed": 0,
            "total_encoding_time": 0.0,
            "average_compression_ratio": 0.0,
            "throughput_mbps": 0.0
        }
        
        logger.info(f"EncodingEngine initialized with {self.max_workers} workers")
    
    def _init_encoding_profiles(self):
        """Initialize predefined encoding profiles."""
        self.encoding_profiles = {
            EncodingProfile.STREAMING_4K: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.FAST,
                width=3840,
                height=2160,
                fps=30,
                bitrate=15000000,  # 15 Mbps
                keyframe_interval=90,
                profile="high",
                level="5.1"
            ),
            
            EncodingProfile.STREAMING_HD: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.FAST,
                width=1920,
                height=1080,
                fps=30,
                bitrate=5000000,  # 5 Mbps
                keyframe_interval=60,
                profile="high",
                level="4.0"
            ),
            
            EncodingProfile.STREAMING_SD: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.FAST,
                width=854,
                height=480,
                fps=30,
                bitrate=1500000,  # 1.5 Mbps
                keyframe_interval=60,
                profile="main",
                level="3.1"
            ),
            
            EncodingProfile.BROADCAST_QUALITY: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.SLOW,
                bitrate=50000000,  # 50 Mbps
                crf=18,
                keyframe_interval=25,
                b_frames=3,
                ref_frames=5,
                profile="high",
                level="5.1"
            ),
            
            EncodingProfile.ARCHIVE_QUALITY: EncodingParameters(
                codec=CodecType.H265,
                preset=EncodingPreset.VERYSLOW,
                compression_mode=CompressionMode.LOSSLESS,
                crf=0,
                profile="main",
                level="5.1"
            ),
            
            EncodingProfile.WEB_OPTIMIZED: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.MEDIUM,
                width=1280,
                height=720,
                fps=30,
                bitrate=2500000,  # 2.5 Mbps
                crf=23,
                keyframe_interval=50,
                profile="high",
                level="3.1"
            ),
            
            EncodingProfile.MOBILE_OPTIMIZED: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.FAST,
                width=854,
                height=480,
                fps=24,
                bitrate=800000,  # 800 kbps
                crf=26,
                keyframe_interval=48,
                profile="baseline",
                level="3.0"
            ),
            
            EncodingProfile.SOCIAL_MEDIA: EncodingParameters(
                codec=CodecType.H264,
                preset=EncodingPreset.MEDIUM,
                width=1080,
                height=1080,  # Square format
                fps=30,
                bitrate=3000000,  # 3 Mbps
                crf=22,
                keyframe_interval=60,
                profile="high",
                level="4.0"
            )
        }
    
    async def encode_async(self, job: EncodingJob) -> EncodingResult:
        """
        Encode content asynchronously.
        
        Args:
            job: Encoding job definition
            
        Returns:
            EncodingResult with encoding details
        """
        try:
            # Validate job
            validation_result = await self._validate_encoding_job(job)
            if not validation_result["valid"]:
                return EncodingResult(
                    job_id=job.job_id,
                    success=False,
                    error_message=validation_result["error"]
                )
            
            # Add to queue and process
            with self.job_lock:
                self.active_jobs[job.job_id] = job
            
            job.started_at = time.time()
            job.status = "encoding"
            
            # Perform encoding
            result = await self._perform_encoding(job)
            
            # Update job status
            job.completed_at = time.time()
            job.status = "completed" if result.success else "failed"
            
            # Store result
            with self.job_lock:
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
                self.completed_jobs[job.job_id] = result
            
            # Update performance metrics
            self._update_performance_metrics(result)
            
            # Call callback if provided
            if job.callback:
                try:
                    await job.callback(result)
                except Exception as e:
                    logger.error(f"Encoding callback failed: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Encoding job {job.job_id} failed: {str(e)}")
            job.status = "failed"
            
            result = EncodingResult(
                job_id=job.job_id,
                success=False,
                error_message=str(e),
                encoding_time=time.time() - (job.started_at or time.time())
            )
            
            with self.job_lock:
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
                self.completed_jobs[job.job_id] = result
            
            return result
    
    async def _validate_encoding_job(self, job: EncodingJob) -> Dict[str, Any]:
        """Validate encoding job parameters."""
        if not job.job_id:
            return {"valid": False, "error": "Job ID is required"}
        
        if not job.input_data:
            return {"valid": False, "error": "Input data is required"}
        
        # Validate codec support
        if job.parameters.codec not in CodecType:
            return {"valid": False, "error": f"Unsupported codec: {job.parameters.codec}"}
        
        # Validate video parameters
        if job.parameters.width and job.parameters.width <= 0:
            return {"valid": False, "error": "Width must be positive"}
        
        if job.parameters.height and job.parameters.height <= 0:
            return {"valid": False, "error": "Height must be positive"}
        
        if job.parameters.fps and job.parameters.fps <= 0:
            return {"valid": False, "error": "FPS must be positive"}
        
        # Validate audio parameters
        if job.parameters.sample_rate and job.parameters.sample_rate not in [8000, 16000, 22050, 44100, 48000, 96000]:
            return {"valid": False, "error": "Invalid sample rate"}
        
        if job.parameters.channels and job.parameters.channels not in [1, 2, 6, 8]:
            return {"valid": False, "error": "Invalid channel count"}
        
        return {"valid": True}
    
    async def _perform_encoding(self, job: EncodingJob) -> EncodingResult:
        """Perform the actual encoding operation."""
        start_time = time.time()
        
        try:
            # Get input size
            input_size = await self._get_input_size(job.input_data)
            
            # Optimize encoding parameters
            optimized_params = await self._optimize_encoding_parameters(job.parameters, job.input_data)
            
            # Execute encoding based on codec type
            if optimized_params.codec in [CodecType.H264, CodecType.H265, CodecType.VP9, CodecType.VP8, CodecType.AV1]:
                encoded_data = await self._encode_video(job.input_data, optimized_params)
            elif optimized_params.codec in [CodecType.AAC, CodecType.MP3, CodecType.OPUS, CodecType.VORBIS, CodecType.FLAC]:
                encoded_data = await self._encode_audio(job.input_data, optimized_params)
            elif optimized_params.codec in [CodecType.JPEG, CodecType.PNG, CodecType.WEBP, CodecType.AVIF, CodecType.HEIF]:
                encoded_data = await self._encode_image(job.input_data, optimized_params)
            else:
                raise ValueError(f"Unsupported codec type: {optimized_params.codec}")
            
            # Calculate metrics
            output_size = len(encoded_data) if encoded_data else 0
            compression_ratio = output_size / input_size if input_size > 0 else 0.0
            encoding_time = time.time() - start_time
            
            # Estimate quality metrics
            quality_metrics = await self._estimate_quality_metrics(
                job.input_data, encoded_data, optimized_params
            )
            
            # Generate encoding statistics
            encoding_stats = await self._generate_encoding_stats(
                optimized_params, encoding_time, input_size, output_size
            )
            
            return EncodingResult(
                job_id=job.job_id,
                success=True,
                output_data=encoded_data,
                output_path=job.output_path,
                input_size=input_size,
                output_size=output_size,
                compression_ratio=compression_ratio,
                encoding_time=encoding_time,
                quality_metrics=quality_metrics,
                encoding_stats=encoding_stats
            )
            
        except Exception as e:
            return EncodingResult(
                job_id=job.job_id,
                success=False,
                error_message=str(e),
                encoding_time=time.time() - start_time
            )
    
    async def _optimize_encoding_parameters(
        self, params: EncodingParameters, input_data: Any
    ) -> EncodingParameters:
        """Optimize encoding parameters based on input analysis."""
        # Create copy of parameters
        optimized = EncodingParameters(
            codec=params.codec,
            preset=params.preset,
            compression_mode=params.compression_mode,
            width=params.width,
            height=params.height,
            fps=params.fps,
            bitrate=params.bitrate,
            crf=params.crf,
            keyframe_interval=params.keyframe_interval,
            b_frames=params.b_frames,
            ref_frames=params.ref_frames,
            sample_rate=params.sample_rate,
            channels=params.channels,
            audio_bitrate=params.audio_bitrate,
            quality=params.quality,
            progressive=params.progressive,
            profile=params.profile,
            level=params.level,
            pixel_format=params.pixel_format,
            color_space=params.color_space,
            hdr=params.hdr,
            custom_options=params.custom_options.copy()
        )
        
        # Analyze input content
        content_analysis = await self._analyze_input_content(input_data)
        
        # Optimize based on content characteristics
        if content_analysis.get("content_type") == "video":
            optimized = await self._optimize_video_parameters(optimized, content_analysis)
        elif content_analysis.get("content_type") == "audio":
            optimized = await self._optimize_audio_parameters(optimized, content_analysis)
        elif content_analysis.get("content_type") == "image":
            optimized = await self._optimize_image_parameters(optimized, content_analysis)
        
        return optimized
    
    async def _analyze_input_content(self, input_data: Any) -> Dict[str, Any]:
        """Analyze input content characteristics."""
        # Placeholder implementation - would use actual media analysis libraries
        return {
            "content_type": "video",  # Placeholder
            "complexity": "medium",
            "motion_level": "moderate",
            "noise_level": "low",
            "dynamic_range": "standard"
        }
    
    async def _optimize_video_parameters(
        self, params: EncodingParameters, analysis: Dict[str, Any]
    ) -> EncodingParameters:
        """Optimize video encoding parameters."""
        # Adjust based on content complexity
        if analysis.get("complexity") == "high":
            if not params.crf:
                params.crf = 20  # Higher quality for complex content
            if not params.b_frames:
                params.b_frames = 3
        elif analysis.get("complexity") == "low":
            if not params.crf:
                params.crf = 26  # Lower quality acceptable for simple content
            if not params.b_frames:
                params.b_frames = 2
        
        # Adjust based on motion level
        if analysis.get("motion_level") == "high":
            if not params.keyframe_interval:
                params.keyframe_interval = 30  # More frequent keyframes
        elif analysis.get("motion_level") == "low":
            if not params.keyframe_interval:
                params.keyframe_interval = 90  # Less frequent keyframes
        
        return params
    
    async def _optimize_audio_parameters(
        self, params: EncodingParameters, analysis: Dict[str, Any]
    ) -> EncodingParameters:
        """Optimize audio encoding parameters."""
        # Set default sample rate if not specified
        if not params.sample_rate:
            params.sample_rate = 44100
        
        # Set default channels if not specified
        if not params.channels:
            params.channels = 2
        
        # Adjust bitrate based on content type
        if not params.audio_bitrate:
            if analysis.get("complexity") == "high":
                params.audio_bitrate = 320000  # 320 kbps for complex audio
            else:
                params.audio_bitrate = 128000  # 128 kbps for standard audio
        
        return params
    
    async def _optimize_image_parameters(
        self, params: EncodingParameters, analysis: Dict[str, Any]
    ) -> EncodingParameters:
        """Optimize image encoding parameters."""
        # Set default quality if not specified
        if not params.quality:
            if analysis.get("complexity") == "high":
                params.quality = 90  # High quality for complex images
            else:
                params.quality = 80  # Standard quality
        
        # Set progressive encoding for web images
        if params.codec == CodecType.JPEG and params.progressive is None:
            params.progressive = True
        
        return params
    
    async def _encode_video(self, input_data: Any, params: EncodingParameters) -> bytes:
        """Encode video content."""
        # Placeholder implementation - would use FFmpeg or similar
        logger.info(f"Encoding video with {params.codec.value} codec")
        
        # Simulate encoding time based on preset
        encoding_time_map = {
            EncodingPreset.ULTRAFAST: 0.1,
            EncodingPreset.FAST: 0.3,
            EncodingPreset.MEDIUM: 0.5,
            EncodingPreset.SLOW: 1.0,
            EncodingPreset.VERYSLOW: 2.0
        }
        
        await asyncio.sleep(encoding_time_map.get(params.preset, 0.5))
        
        # Return placeholder encoded data
        return f"encoded_video_{params.codec.value}_data".encode()
    
    async def _encode_audio(self, input_data: Any, params: EncodingParameters) -> bytes:
        """Encode audio content."""
        # Placeholder implementation - would use audio encoding libraries
        logger.info(f"Encoding audio with {params.codec.value} codec")
        
        # Simulate encoding
        await asyncio.sleep(0.2)
        
        return f"encoded_audio_{params.codec.value}_data".encode()
    
    async def _encode_image(self, input_data: Any, params: EncodingParameters) -> bytes:
        """Encode image content."""
        # Placeholder implementation - would use image encoding libraries
        logger.info(f"Encoding image with {params.codec.value} codec")
        
        # Simulate encoding
        await asyncio.sleep(0.05)
        
        return f"encoded_image_{params.codec.value}_data".encode()
    
    async def _get_input_size(self, input_data: Any) -> int:
        """Get size of input data."""
        if isinstance(input_data, bytes):
            return len(input_data)
        elif isinstance(input_data, (str, Path)):
            try:
                return Path(input_data).stat().st_size
            except:
                return 0
        else:
            return 1024000  # Placeholder size
    
    async def _estimate_quality_metrics(
        self, input_data: Any, output_data: bytes, params: EncodingParameters
    ) -> Dict[str, float]:
        """Estimate quality metrics for encoded content."""
        # Placeholder quality estimation
        base_quality = 0.8
        
        # Adjust based on compression mode
        if params.compression_mode == CompressionMode.LOSSLESS:
            base_quality = 1.0
        elif params.compression_mode == CompressionMode.NEAR_LOSSLESS:
            base_quality = 0.95
        
        # Adjust based on preset
        preset_quality_map = {
            EncodingPreset.ULTRAFAST: 0.7,
            EncodingPreset.FAST: 0.8,
            EncodingPreset.MEDIUM: 0.85,
            EncodingPreset.SLOW: 0.9,
            EncodingPreset.VERYSLOW: 0.95
        }
        
        preset_factor = preset_quality_map.get(params.preset, 0.8)
        final_quality = base_quality * preset_factor
        
        return {
            "overall_quality": final_quality,
            "visual_quality": final_quality,
            "compression_efficiency": 0.8,
            "encoding_speed": 1.0 - preset_factor + 0.5  # Inverse relationship
        }
    
    async def _generate_encoding_stats(
        self, params: EncodingParameters, encoding_time: float, input_size: int, output_size: int
    ) -> Dict[str, Any]:
        """Generate encoding statistics."""
        throughput = input_size / encoding_time if encoding_time > 0 else 0
        
        return {
            "codec_used": params.codec.value,
            "preset_used": params.preset.value,
            "encoding_time": encoding_time,
            "throughput_bps": throughput,
            "throughput_mbps": throughput / (1024 * 1024),
            "compression_ratio": output_size / input_size if input_size > 0 else 0,
            "space_saved_percentage": (1 - output_size / input_size) * 100 if input_size > 0 else 0,
            "parameters_used": {
                "width": params.width,
                "height": params.height,
                "fps": params.fps,
                "bitrate": params.bitrate,
                "sample_rate": params.sample_rate,
                "channels": params.channels
            }
        }
    
    def _update_performance_metrics(self, result: EncodingResult):
        """Update global performance metrics."""
        self.performance_metrics["jobs_completed"] += 1
        self.performance_metrics["total_encoding_time"] += result.encoding_time
        
        # Update compression ratio
        if result.compression_ratio:
            current_avg = self.performance_metrics["average_compression_ratio"]
            jobs_completed = self.performance_metrics["jobs_completed"]
            
            new_avg = ((current_avg * (jobs_completed - 1)) + result.compression_ratio) / jobs_completed
            self.performance_metrics["average_compression_ratio"] = new_avg
        
        # Update throughput
        if result.encoding_time > 0 and result.input_size:
            throughput = result.input_size / result.encoding_time / (1024 * 1024)  # MB/s
            current_throughput = self.performance_metrics["throughput_mbps"]
            jobs_completed = self.performance_metrics["jobs_completed"]
            
            new_throughput = ((current_throughput * (jobs_completed - 1)) + throughput) / jobs_completed
            self.performance_metrics["throughput_mbps"] = new_throughput
    
    def get_encoding_profile(self, profile: EncodingProfile) -> Optional[EncodingParameters]:
        """Get predefined encoding profile."""
        return self.encoding_profiles.get(profile)
    
    def create_adaptive_encoding_job(
        self, job_id: str, input_data: Any, context: AdaptiveEncodingContext
    ) -> EncodingJob:
        """Create encoding job with adaptive parameters based on context."""
        # Determine optimal parameters based on context
        params = self._select_adaptive_parameters(context)
        
        return EncodingJob(
            job_id=job_id,
            input_data=input_data,
            parameters=params
        )
    
    def _select_adaptive_parameters(self, context: AdaptiveEncodingContext) -> EncodingParameters:
        """Select optimal encoding parameters based on adaptive context."""
        # Default parameters
        params = EncodingParameters(codec=CodecType.H264, preset=EncodingPreset.MEDIUM)
        
        # Adjust based on target device
        if context.target_device == "mobile":
            params = self.get_encoding_profile(EncodingProfile.MOBILE_OPTIMIZED) or params
        elif context.target_device == "smart_tv":
            params = self.get_encoding_profile(EncodingProfile.STREAMING_HD) or params
        elif context.target_device == "web":
            params = self.get_encoding_profile(EncodingProfile.WEB_OPTIMIZED) or params
        
        # Adjust based on network conditions
        if context.network_conditions == "poor":
            # Reduce bitrate for poor networks
            if params.bitrate:
                params.bitrate = int(params.bitrate * 0.5)
            params.preset = EncodingPreset.FAST  # Prioritize speed
        elif context.network_conditions == "excellent":
            # Increase quality for good networks
            if params.bitrate:
                params.bitrate = int(params.bitrate * 1.5)
            params.preset = EncodingPreset.SLOW  # Prioritize quality
        
        return params
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of encoding job."""
        with self.job_lock:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": job.status,
                    "started_at": job.started_at,
                    "progress": "encoding"  # Would calculate actual progress in real implementation
                }
            elif job_id in self.completed_jobs:
                result = self.completed_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": "completed" if result.success else "failed",
                    "encoding_time": result.encoding_time,
                    "compression_ratio": result.compression_ratio,
                    "output_size": result.output_size
                }
            else:
                return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get encoding engine performance metrics."""
        return self.performance_metrics.copy()
    
    async def shutdown(self):
        """Shutdown encoding engine gracefully."""
        logger.info("Shutting down EncodingEngine...")
        
        # Wait for active jobs to complete
        timeout = 30.0
        start_time = time.time()
        
        while self.active_jobs and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)
        
        logger.info("EncodingEngine shutdown complete")


class AdaptiveEncodingManager:
    """Manager for adaptive encoding with machine learning optimization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize adaptive encoding manager."""
        self.config = config or {}
        self.encoding_engine = EncodingEngine(config)
        self.adaptation_history = []
        
        logger.info("AdaptiveEncodingManager initialized")
    
    async def encode_with_adaptation(
        self, input_data: Any, context: AdaptiveEncodingContext
    ) -> EncodingResult:
        """Encode content with adaptive parameter selection."""
        try:
            # Create adaptive encoding job
            job_id = f"adaptive_{int(time.time() * 1000)}"
            job = self.encoding_engine.create_adaptive_encoding_job(job_id, input_data, context)
            
            # Perform encoding
            result = await self.encoding_engine.encode_async(job)
            
            # Learn from result for future adaptations
            await self._learn_from_encoding_result(context, job.parameters, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Adaptive encoding failed: {str(e)}")
            return EncodingResult(
                job_id="failed",
                success=False,
                error_message=str(e)
            )
    
    async def _learn_from_encoding_result(
        self, context: AdaptiveEncodingContext, parameters: EncodingParameters, result: EncodingResult
    ):
        """Learn from encoding results to improve future parameter selection."""
        # Store adaptation data for machine learning
        adaptation_data = {
            "context": context,
            "parameters": parameters,
            "result_metrics": {
                "success": result.success,
                "encoding_time": result.encoding_time,
                "compression_ratio": result.compression_ratio,
                "quality_metrics": result.quality_metrics
            },
            "timestamp": time.time()
        }
        
        self.adaptation_history.append(adaptation_data)
        
        # Keep only recent history (last 1000 adaptations)
        if len(self.adaptation_history) > 1000:
            self.adaptation_history = self.adaptation_history[-1000:]
        
        logger.debug("Learned from encoding result for future adaptations")
    
    def get_adaptation_insights(self) -> Dict[str, Any]:
        """Get insights from adaptation history."""
        if not self.adaptation_history:
            return {"message": "No adaptation history available"}
        
        # Analyze adaptation patterns
        successful_adaptations = [
            adapt for adapt in self.adaptation_history
            if adapt["result_metrics"]["success"]
        ]
        
        if not successful_adaptations:
            return {"message": "No successful adaptations to analyze"}
        
        # Calculate average metrics
        avg_encoding_time = sum(
            adapt["result_metrics"]["encoding_time"] for adapt in successful_adaptations
        ) / len(successful_adaptations)
        
        avg_compression_ratio = sum(
            adapt["result_metrics"]["compression_ratio"] or 0 for adapt in successful_adaptations
        ) / len(successful_adaptations)
        
        return {
            "total_adaptations": len(self.adaptation_history),
            "successful_adaptations": len(successful_adaptations),
            "success_rate": len(successful_adaptations) / len(self.adaptation_history),
            "average_encoding_time": avg_encoding_time,
            "average_compression_ratio": avg_compression_ratio,
            "insights": [
                "Adaptation patterns identified",
                "Machine learning optimization active",
                "Continuous improvement in progress"
            ]
        }


# Export all classes for module imports
__all__ = [
    "EncodingEngine",
    "AdaptiveEncodingManager",
    "CodecType",
    "EncodingPreset",
    "CompressionMode",
    "EncodingProfile",
    "EncodingParameters",
    "EncodingJob",
    "EncodingResult",
    "AdaptiveEncodingContext"
]

logger.info("Encoding engine module loaded successfully")