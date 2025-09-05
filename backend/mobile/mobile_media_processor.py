"""Mobile Media Processor
========================

Mobile-optimized media processing pipeline with adaptive quality,
format conversion, and creator-specific optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Media processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityLevel(str, Enum):
    """Quality levels for mobile optimization."""
    ULTRA_LOW = "ultra_low"      # For 2G/limited bandwidth
    LOW = "low"                  # For 3G/battery saving
    MEDIUM = "medium"            # For 4G/balanced
    HIGH = "high"                # For WiFi/high-end devices
    ULTRA_HIGH = "ultra_high"    # For WiFi/premium content
    ADAPTIVE = "adaptive"        # Auto-adjust based on conditions


class MobileFormat(str, Enum):
    """Mobile-optimized output formats."""
    # Video
    MP4_H264 = "mp4_h264"       # Universal compatibility
    MP4_H265 = "mp4_h265"       # Better compression
    WEBM_VP9 = "webm_vp9"       # Web optimized
    
    # Audio
    AAC_128 = "aac_128"         # Standard quality
    AAC_256 = "aac_256"         # High quality
    MP3_192 = "mp3_192"         # Compatibility
    OPUS = "opus"               # Best compression
    
    # Image
    WEBP = "webp"               # Best web format
    AVIF = "avif"               # Next-gen format
    JPEG_OPTIMIZED = "jpeg_opt" # Optimized JPEG
    PNG_OPTIMIZED = "png_opt"   # Optimized PNG


class ProcessingPriority(str, Enum):
    """Processing priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class MobileProcessingSettings:
    """Mobile-specific processing settings."""
    target_quality: QualityLevel
    output_formats: List[MobileFormat]
    max_resolution: Tuple[int, int]  # (width, height)
    max_bitrate_kbps: int
    frame_rate: float
    audio_sample_rate: int
    enable_hardware_acceleration: bool = True
    preserve_metadata: bool = True
    create_thumbnails: bool = True
    create_previews: bool = True
    adaptive_streaming: bool = False
    progressive_download: bool = True
    mobile_optimizations: List[str] = None
    battery_efficient: bool = True
    network_aware: bool = True

    def __post_init__(self):
        if self.mobile_optimizations is None:
            self.mobile_optimizations = [
                "size_optimization",
                "format_optimization",
                "streaming_optimization"
            ]


@dataclass
class ProcessingRequest:
    """Media processing request."""
    request_id: str
    creator_id: str
    creator_type: str
    input_file_path: str
    content_type: str  # audio, video, image
    mobile_device_id: str
    device_type: str
    network_type: str
    processing_settings: MobileProcessingSettings
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    metadata: Dict[str, Any] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessingResult:
    """Media processing result."""
    request_id: str
    status: ProcessingStatus
    output_files: Dict[str, str]  # format -> file_path
    thumbnails: List[str]
    previews: List[str]
    processing_time_seconds: float
    file_size_reduction_percent: float
    quality_metrics: Dict[str, Any]
    mobile_optimizations_applied: List[str]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    completed_at: datetime = None

    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class MobileMediaProcessor:
    """Mobile-optimized media processing pipeline."""

    def __init__(self, temp_dir: str = "/tmp/mobile_processing"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.processing_queue: Dict[str, ProcessingRequest] = {}
        self.processing_results: Dict[str, ProcessingResult] = {}
        self.active_processing: Dict[str, asyncio.Task] = {}
        
        # Initialize processing components
        self.quality_profiles = self._initialize_quality_profiles()
        self.format_processors = self._initialize_format_processors()
        self.mobile_optimizers = self._initialize_mobile_optimizers()
        self.creator_presets = self._initialize_creator_presets()

    def _initialize_quality_profiles(self) -> Dict[QualityLevel, Dict[str, Any]]:
        """Initialize quality profiles for different mobile conditions."""
        return {
            QualityLevel.ULTRA_LOW: {
                "video": {"width": 240, "height": 160, "bitrate": 100, "fps": 15},
                "audio": {"bitrate": 32, "sample_rate": 22050},
                "image": {"quality": 30, "max_width": 400}
            },
            QualityLevel.LOW: {
                "video": {"width": 480, "height": 320, "bitrate": 300, "fps": 24},
                "audio": {"bitrate": 64, "sample_rate": 44100},
                "image": {"quality": 50, "max_width": 800}
            },
            QualityLevel.MEDIUM: {
                "video": {"width": 720, "height": 480, "bitrate": 800, "fps": 30},
                "audio": {"bitrate": 128, "sample_rate": 44100},
                "image": {"quality": 70, "max_width": 1200}
            },
            QualityLevel.HIGH: {
                "video": {"width": 1280, "height": 720, "bitrate": 2000, "fps": 30},
                "audio": {"bitrate": 256, "sample_rate": 48000},
                "image": {"quality": 85, "max_width": 1920}
            },
            QualityLevel.ULTRA_HIGH: {
                "video": {"width": 1920, "height": 1080, "bitrate": 5000, "fps": 60},
                "audio": {"bitrate": 320, "sample_rate": 48000},
                "image": {"quality": 95, "max_width": 3840}
            }
        }

    def _initialize_format_processors(self) -> Dict[str, Any]:
        """Initialize format-specific processors."""
        return {
            "video": self._create_video_processor(),
            "audio": self._create_audio_processor(),
            "image": self._create_image_processor()
        }

    def _initialize_mobile_optimizers(self) -> Dict[str, Any]:
        """Initialize mobile optimization modules."""
        return {
            "size_optimization": self._create_size_optimizer(),
            "format_optimization": self._create_format_optimizer(),
            "streaming_optimization": self._create_streaming_optimizer(),
            "battery_optimization": self._create_battery_optimizer(),
            "network_optimization": self._create_network_optimizer()
        }

    def _initialize_creator_presets(self) -> Dict[str, MobileProcessingSettings]:
        """Initialize creator-specific processing presets."""
        return {
            "musician": MobileProcessingSettings(
                target_quality=QualityLevel.HIGH,
                output_formats=[MobileFormat.AAC_256, MobileFormat.MP3_192],
                max_resolution=(0, 0),  # Audio only
                max_bitrate_kbps=256,
                frame_rate=0,
                audio_sample_rate=48000,
                mobile_optimizations=["size_optimization", "streaming_optimization"]
            ),
            "blogger": MobileProcessingSettings(
                target_quality=QualityLevel.MEDIUM,
                output_formats=[MobileFormat.WEBP, MobileFormat.JPEG_OPTIMIZED],
                max_resolution=(1200, 800),
                max_bitrate_kbps=0,  # Image only
                frame_rate=0,
                audio_sample_rate=0,
                mobile_optimizations=["format_optimization", "size_optimization"]
            ),
            "photographer": MobileProcessingSettings(
                target_quality=QualityLevel.HIGH,
                output_formats=[MobileFormat.WEBP, MobileFormat.AVIF],
                max_resolution=(1920, 1080),
                max_bitrate_kbps=0,  # Image only
                frame_rate=0,
                audio_sample_rate=0,
                mobile_optimizations=["format_optimization", "size_optimization"]
            ),
            "influencer": MobileProcessingSettings(
                target_quality=QualityLevel.HIGH,
                output_formats=[MobileFormat.MP4_H264, MobileFormat.WEBP],
                max_resolution=(1280, 720),
                max_bitrate_kbps=2000,
                frame_rate=30,
                audio_sample_rate=44100,
                mobile_optimizations=["streaming_optimization", "network_optimization"]
            ),
            "comedian": MobileProcessingSettings(
                target_quality=QualityLevel.MEDIUM,
                output_formats=[MobileFormat.MP4_H264, MobileFormat.AAC_128],
                max_resolution=(720, 480),
                max_bitrate_kbps=800,
                frame_rate=24,
                audio_sample_rate=44100,
                mobile_optimizations=["size_optimization", "battery_optimization"]
            )
        }

    async def submit_processing_request(self, request: ProcessingRequest) -> str:
        """Submit a media processing request."""
        try:
            logger.info(f"Submitting processing request {request.request_id}")
            
            # Apply creator-specific presets if no settings provided
            if not hasattr(request, 'processing_settings') or not request.processing_settings:
                preset = self.creator_presets.get(request.creator_type)
                if preset:
                    request.processing_settings = preset
                else:
                    raise ValueError(f"No processing settings for creator type {request.creator_type}")
            
            # Optimize settings for mobile device and network
            optimized_settings = await self._optimize_settings_for_mobile(request)
            request.processing_settings = optimized_settings
            
            # Add to processing queue
            self.processing_queue[request.request_id] = request
            
            # Start processing if high priority
            if request.priority in [ProcessingPriority.HIGH, ProcessingPriority.URGENT]:
                await self._start_processing(request.request_id)
            
            logger.info(f"Processing request {request.request_id} queued")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Failed to submit processing request: {e}")
            raise

    async def start_processing(self, request_id: str) -> bool:
        """Start processing a queued request."""
        if request_id not in self.processing_queue:
            return False
        
        await self._start_processing(request_id)
        return True

    async def _start_processing(self, request_id: str) -> None:
        """Start asynchronous processing of a request."""
        if request_id in self.active_processing:
            return  # Already processing
        
        request = self.processing_queue[request_id]
        
        # Create processing task
        task = asyncio.create_task(self._process_media(request))
        self.active_processing[request_id] = task
        
        logger.info(f"Started processing {request_id}")

    async def _process_media(self, request: ProcessingRequest) -> ProcessingResult:
        """Process media with mobile optimizations."""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Processing media for request {request.request_id}")
            
            # Initialize result
            result = ProcessingResult(
                request_id=request.request_id,
                status=ProcessingStatus.PROCESSING,
                output_files={},
                thumbnails=[],
                previews=[],
                processing_time_seconds=0.0,
                file_size_reduction_percent=0.0,
                quality_metrics={},
                mobile_optimizations_applied=request.processing_settings.mobile_optimizations
            )
            
            # Get input file info
            input_path = Path(request.input_file_path)
            original_size = input_path.stat().st_size
            
            # Create working directory
            work_dir = self.temp_dir / request.request_id
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # Apply mobile optimizations
            for optimization in request.processing_settings.mobile_optimizations:
                await self._apply_mobile_optimization(request, work_dir, optimization)
            
            # Process based on content type
            if request.content_type == "video":
                output_files = await self._process_video(request, work_dir)
                thumbnails = await self._generate_video_thumbnails(request, work_dir)
                previews = await self._generate_video_previews(request, work_dir)
            elif request.content_type == "audio":
                output_files = await self._process_audio(request, work_dir)
                thumbnails = await self._generate_audio_thumbnails(request, work_dir)
                previews = []
            elif request.content_type == "image":
                output_files = await self._process_image(request, work_dir)
                thumbnails = []
                previews = []
            else:
                raise ValueError(f"Unsupported content type: {request.content_type}")
            
            # Calculate metrics
            total_output_size = sum(
                Path(path).stat().st_size for path in output_files.values()
                if Path(path).exists()
            )
            
            size_reduction = ((original_size - total_output_size) / original_size) * 100
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Generate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                request, output_files, original_size, total_output_size
            )
            
            # Update result
            result.status = ProcessingStatus.COMPLETED
            result.output_files = output_files
            result.thumbnails = thumbnails
            result.previews = previews
            result.processing_time_seconds = processing_time
            result.file_size_reduction_percent = size_reduction
            result.quality_metrics = quality_metrics
            
            # Store result
            self.processing_results[request.request_id] = result
            
            # Clean up
            if request.request_id in self.active_processing:
                del self.active_processing[request.request_id]
            if request.request_id in self.processing_queue:
                del self.processing_queue[request.request_id]
            
            logger.info(f"Processing completed for {request.request_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Processing failed for {request.request_id}: {e}")
            
            # Create error result
            error_result = ProcessingResult(
                request_id=request.request_id,
                status=ProcessingStatus.FAILED,
                output_files={},
                thumbnails=[],
                previews=[],
                processing_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
                file_size_reduction_percent=0.0,
                quality_metrics={},
                mobile_optimizations_applied=[],
                error_message=str(e)
            )
            
            self.processing_results[request.request_id] = error_result
            
            # Clean up
            if request.request_id in self.active_processing:
                del self.active_processing[request.request_id]
            
            return error_result

    async def _optimize_settings_for_mobile(self, request: ProcessingRequest) -> MobileProcessingSettings:
        """Optimize processing settings for mobile device and network."""
        settings = request.processing_settings
        
        # Network-based optimizations
        if request.network_type in ["2g", "limited"]:
            settings.target_quality = QualityLevel.ULTRA_LOW
            settings.max_bitrate_kbps = min(settings.max_bitrate_kbps, 100)
        elif request.network_type == "3g":
            settings.target_quality = QualityLevel.LOW
            settings.max_bitrate_kbps = min(settings.max_bitrate_kbps, 300)
        elif request.network_type == "4g":
            settings.target_quality = QualityLevel.MEDIUM
        
        # Device-based optimizations
        if request.device_type == "ios":
            # Prefer H.264 for iOS compatibility
            if MobileFormat.MP4_H265 in settings.output_formats:
                settings.output_formats.append(MobileFormat.MP4_H264)
        
        # Apply quality profile limits
        quality_profile = self.quality_profiles.get(settings.target_quality, {})
        if request.content_type in quality_profile:
            profile = quality_profile[request.content_type]
            
            if "width" in profile and "height" in profile:
                max_width = min(settings.max_resolution[0], profile["width"])
                max_height = min(settings.max_resolution[1], profile["height"])
                settings.max_resolution = (max_width, max_height)
            
            if "bitrate" in profile:
                settings.max_bitrate_kbps = min(settings.max_bitrate_kbps, profile["bitrate"])
        
        return settings

    async def _apply_mobile_optimization(self, request: ProcessingRequest, 
                                        work_dir: Path, optimization: str) -> None:
        """Apply specific mobile optimization."""
        optimizer = self.mobile_optimizers.get(optimization)
        if optimizer:
            logger.debug(f"Applying {optimization} optimization")
            # Actual optimization logic would be implemented here

    async def _process_video(self, request: ProcessingRequest, work_dir: Path) -> Dict[str, str]:
        """Process video with mobile optimizations."""
        output_files = {}
        
        for format_type in request.processing_settings.output_formats:
            if format_type in [MobileFormat.MP4_H264, MobileFormat.MP4_H265, MobileFormat.WEBM_VP9]:
                output_path = work_dir / f"output_{format_type.value}.{format_type.value.split('_')[0]}"
                
                # Placeholder for actual video processing
                # Would use FFmpeg or similar tool for actual processing
                await self._simulate_video_processing(request, output_path, format_type)
                output_files[format_type.value] = str(output_path)
        
        return output_files

    async def _process_audio(self, request: ProcessingRequest, work_dir: Path) -> Dict[str, str]:
        """Process audio with mobile optimizations."""
        output_files = {}
        
        for format_type in request.processing_settings.output_formats:
            if format_type in [MobileFormat.AAC_128, MobileFormat.AAC_256, MobileFormat.MP3_192, MobileFormat.OPUS]:
                extension = format_type.value.split('_')[0]
                output_path = work_dir / f"output_{format_type.value}.{extension}"
                
                # Placeholder for actual audio processing
                await self._simulate_audio_processing(request, output_path, format_type)
                output_files[format_type.value] = str(output_path)
        
        return output_files

    async def _process_image(self, request: ProcessingRequest, work_dir: Path) -> Dict[str, str]:
        """Process image with mobile optimizations."""
        output_files = {}
        
        for format_type in request.processing_settings.output_formats:
            if format_type in [MobileFormat.WEBP, MobileFormat.AVIF, MobileFormat.JPEG_OPTIMIZED, MobileFormat.PNG_OPTIMIZED]:
                extension = format_type.value.split('_')[0] if '_' in format_type.value else format_type.value
                output_path = work_dir / f"output_{format_type.value}.{extension}"
                
                # Placeholder for actual image processing
                await self._simulate_image_processing(request, output_path, format_type)
                output_files[format_type.value] = str(output_path)
        
        return output_files

    async def _generate_video_thumbnails(self, request: ProcessingRequest, work_dir: Path) -> List[str]:
        """Generate video thumbnails."""
        thumbnails = []
        if request.processing_settings.create_thumbnails:
            # Generate thumbnails at different time points
            for i, time_point in enumerate([0.1, 0.3, 0.5, 0.7, 0.9]):  # 10%, 30%, etc.
                thumb_path = work_dir / f"thumbnail_{i}.jpg"
                # Placeholder for actual thumbnail generation
                await self._simulate_thumbnail_generation(request, thumb_path, time_point)
                thumbnails.append(str(thumb_path))
        return thumbnails

    async def _generate_audio_thumbnails(self, request: ProcessingRequest, work_dir: Path) -> List[str]:
        """Generate audio waveform thumbnails."""
        thumbnails = []
        if request.processing_settings.create_thumbnails:
            thumb_path = work_dir / "waveform.png"
            # Placeholder for actual waveform generation
            await self._simulate_waveform_generation(request, thumb_path)
            thumbnails.append(str(thumb_path))
        return thumbnails

    async def _generate_video_previews(self, request: ProcessingRequest, work_dir: Path) -> List[str]:
        """Generate video previews."""
        previews = []
        if request.processing_settings.create_previews:
            preview_path = work_dir / "preview.mp4"
            # Placeholder for actual preview generation
            await self._simulate_preview_generation(request, preview_path)
            previews.append(str(preview_path))
        return previews

    async def _calculate_quality_metrics(self, request: ProcessingRequest, 
                                        output_files: Dict[str, str], 
                                        original_size: int, total_output_size: int) -> Dict[str, Any]:
        """Calculate quality metrics for processed media."""
        return {
            "compression_ratio": original_size / total_output_size if total_output_size > 0 else 0,
            "formats_generated": len(output_files),
            "mobile_optimized": True,
            "estimated_quality_score": 85.0,  # Placeholder
            "mobile_compatibility": "high",
            "streaming_optimized": "progressive_download" in request.processing_settings.mobile_optimizations
        }

    # Simulation methods (placeholders for actual processing)
    async def _simulate_video_processing(self, request: ProcessingRequest, output_path: Path, format_type: MobileFormat):
        """Simulate video processing."""
        await asyncio.sleep(0.1)  # Simulate processing time
        output_path.touch()  # Create empty file

    async def _simulate_audio_processing(self, request: ProcessingRequest, output_path: Path, format_type: MobileFormat):
        """Simulate audio processing."""
        await asyncio.sleep(0.1)
        output_path.touch()

    async def _simulate_image_processing(self, request: ProcessingRequest, output_path: Path, format_type: MobileFormat):
        """Simulate image processing."""
        await asyncio.sleep(0.1)
        output_path.touch()

    async def _simulate_thumbnail_generation(self, request: ProcessingRequest, thumb_path: Path, time_point: float):
        """Simulate thumbnail generation."""
        await asyncio.sleep(0.05)
        thumb_path.touch()

    async def _simulate_waveform_generation(self, request: ProcessingRequest, thumb_path: Path):
        """Simulate waveform generation."""
        await asyncio.sleep(0.05)
        thumb_path.touch()

    async def _simulate_preview_generation(self, request: ProcessingRequest, preview_path: Path):
        """Simulate preview generation."""
        await asyncio.sleep(0.1)
        preview_path.touch()

    # Placeholder processor creation methods
    def _create_video_processor(self): return None
    def _create_audio_processor(self): return None
    def _create_image_processor(self): return None
    def _create_size_optimizer(self): return None
    def _create_format_optimizer(self): return None
    def _create_streaming_optimizer(self): return None
    def _create_battery_optimizer(self): return None
    def _create_network_optimizer(self): return None

    async def get_processing_status(self, request_id: str) -> Optional[ProcessingResult]:
        """Get processing status for a request."""
        return self.processing_results.get(request_id)

    async def cancel_processing(self, request_id: str) -> bool:
        """Cancel active processing."""
        if request_id in self.active_processing:
            task = self.active_processing[request_id]
            task.cancel()
            del self.active_processing[request_id]
            
            # Update result
            if request_id in self.processing_results:
                self.processing_results[request_id].status = ProcessingStatus.CANCELLED
            
            return True
        return False

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "queued_requests": len(self.processing_queue),
            "active_processing": len(self.active_processing),
            "completed_requests": len([r for r in self.processing_results.values() if r.status == ProcessingStatus.COMPLETED]),
            "failed_requests": len([r for r in self.processing_results.values() if r.status == ProcessingStatus.FAILED])
        }

    async def get_mobile_processing_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get mobile processing analytics for a creator."""
        creator_results = [
            result for result in self.processing_results.values()
            if result.request_id.startswith(creator_id)  # Assuming request_id includes creator_id
        ]
        
        if not creator_results:
            return {"total_processed": 0}
        
        completed = [r for r in creator_results if r.status == ProcessingStatus.COMPLETED]
        
        return {
            "total_processed": len(creator_results),
            "successful_processing": len(completed),
            "average_processing_time": sum(r.processing_time_seconds for r in completed) / len(completed) if completed else 0,
            "average_size_reduction": sum(r.file_size_reduction_percent for r in completed) / len(completed) if completed else 0,
            "mobile_optimization_usage": self._analyze_mobile_optimization_usage(creator_results),
            "quality_trends": self._analyze_quality_trends(completed),
            "format_preferences": self._analyze_format_preferences(completed)
        }

    def _analyze_mobile_optimization_usage(self, results: List[ProcessingResult]) -> Dict[str, int]:
        """Analyze mobile optimization usage patterns."""
        usage = {}
        for result in results:
            for opt in result.mobile_optimizations_applied:
                usage[opt] = usage.get(opt, 0) + 1
        return usage

    def _analyze_quality_trends(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Analyze quality trends over time."""
        if not results:
            return {}
        
        return {
            "average_quality_score": sum(
                r.quality_metrics.get("estimated_quality_score", 0) for r in results
            ) / len(results),
            "compression_efficiency": sum(
                r.quality_metrics.get("compression_ratio", 0) for r in results
            ) / len(results),
            "mobile_compatibility": "high"  # Placeholder
        }

    def _analyze_format_preferences(self, results: List[ProcessingResult]) -> Dict[str, int]:
        """Analyze format generation preferences."""
        format_usage = {}
        for result in results:
            for format_name in result.output_files.keys():
                format_usage[format_name] = format_usage.get(format_name, 0) + 1
        return format_usage