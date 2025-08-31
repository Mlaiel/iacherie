"""Multimedia Converter - Enterprise Format Conversion Engine

Advanced format conversion system supporting all multimedia formats.
Provides intelligent format detection, conversion, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
import os
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import mimetypes
import magic
from pathlib import Path

# Audio/Video processing
import ffmpeg
from PIL import Image, ImageOps
import cv2
import numpy as np

# Document processing
import pypandoc
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .format_detector import MultimediaFormatDetector
from .metadata import MultimediaMetadata
from .quality import MultimediaQuality

logger = logging.getLogger(__name__)


class ConversionQuality(Enum):
    """Conversion quality levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"
    ULTRA = "ultra"


class ConversionMode(Enum):
    """Conversion processing modes"""    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    BATCH = "batch"
    REALTIME = "realtime"


@dataclass
class ConversionProfile:
    """Multimedia conversion profile"""    profile_id: str
    name: str
    description: str
    source_formats: List[str]
    target_format: str
    quality: ConversionQuality
    mode: ConversionMode
    parameters: Dict[str, Any] = field(default_factory=dict)
    codec_settings: Dict[str, Any] = field(default_factory=dict)
    output_settings: Dict[str, Any] = field(default_factory=dict)
    preprocessing: List[str] = field(default_factory=list)
    postprocessing: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class ConversionRequest:
    """Conversion request specification"""    request_id: str
    source_file: str
    target_format: str
    output_path: Optional[str] = None
    profile: Optional[ConversionProfile] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    quality: ConversionQuality = ConversionQuality.HIGH
    mode: ConversionMode = ConversionMode.BALANCED
    metadata_preservation: bool = True
    watermark_config: Optional[Dict[str, Any]] = None
    thumbnail_generation: bool = False
    progress_callback: Optional[callable] = None


@dataclass
class ConversionResult:
    """Conversion operation result"""    request_id: str
    success: bool
    output_file: Optional[str] = None
    original_format: Optional[str] = None
    target_format: Optional[str] = None
    file_size_original: Optional[int] = None
    file_size_converted: Optional[int] = None
    compression_ratio: Optional[float] = None
    processing_time: Optional[float] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    thumbnails: List[str] = field(default_factory=list)


class MultimediaConverter:
    """Enterprise multimedia format converter"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.format_detector = MultimediaFormatDetector(config.get("detector", {}))
        self.metadata_extractor = MultimediaMetadata(config.get("metadata", {}))
        self.quality_analyzer = MultimediaQuality(config.get("quality", {}))
        
        # Conversion profiles
        self.profiles: Dict[str, ConversionProfile] = {}
        self.default_profiles = self._create_default_profiles()
        
        # Supported conversions matrix
        self.conversion_matrix = self._build_conversion_matrix()
        
        # Configuration
        self.temp_directory = config.get("temp_directory", tempfile.gettempdir())
        self.max_file_size = config.get("max_file_size", 1024 * 1024 * 1024)  # 1GB
        self.parallel_conversions = config.get("parallel_conversions", 4)
        self.cleanup_temp_files = config.get("cleanup_temp_files", True)
        
        # Performance tracking
        self.conversion_stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "formats_converted": {},
            "quality_distribution": {}
        }
        
    async def initialize(self):
        """Initialize converter components"""        try:
            await self.format_detector.initialize()
            await self.metadata_extractor.initialize()
            await self.quality_analyzer.initialize()
            
            # Load conversion profiles
            await self._load_conversion_profiles()
            
            # Verify external tools
            await self._verify_external_tools()
            
            logger.info("Multimedia converter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize converter: {e}")
            raise
            
    async def convert_file(self, request: ConversionRequest) -> ConversionResult:
        """Convert multimedia file to target format"""        start_time = datetime.now()
        
        try:
            # Validate request
            validation_result = await self._validate_conversion_request(request)
            if not validation_result["valid"]:
                return ConversionResult(
                    request_id=request.request_id,
                    success=False,
                    error_details=validation_result["error"]
                )
                
            # Detect source format
            source_format = await self.format_detector.detect_format(request.source_file)
            if not source_format:
                return ConversionResult(
                    request_id=request.request_id,
                    success=False,
                    error_details="Unable to detect source format"
                )
                
            # Check conversion support
            if not self._is_conversion_supported(source_format, request.target_format):
                return ConversionResult(
                    request_id=request.request_id,
                    success=False,
                    error_details=f"Conversion from {source_format} to {request.target_format} not supported"
                )
                
            # Select conversion profile
            profile = request.profile or await self._select_optimal_profile(
                source_format, request.target_format, request.quality
            )
            
            # Extract source metadata
            source_metadata = await self.metadata_extractor.extract_metadata(request.source_file)
            
            # Perform conversion
            conversion_result = await self._perform_conversion(request, profile, source_metadata)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self._update_conversion_stats(source_format, request.target_format, processing_time, True)
            
            return conversion_result
            
        except Exception as e:
            # Handle conversion failure
            processing_time = (datetime.now() - start_time).total_seconds()
            await self._update_conversion_stats("unknown", request.target_format, processing_time, False)
            
            logger.error(f"Conversion failed for request {request.request_id}: {e}")
            
            return ConversionResult(
                request_id=request.request_id,
                success=False,
                error_details=str(e),
                processing_time=processing_time
            )
            
    async def batch_convert(self, requests: List[ConversionRequest]) -> List[ConversionResult]:
        """Convert multiple files in batch"""        try:
            # Create semaphore for parallel processing
            semaphore = asyncio.Semaphore(self.parallel_conversions)
            
            async def convert_with_semaphore(request):
                async with semaphore:
                    return await self.convert_file(request)
                    
            # Process conversions in parallel
            tasks = [convert_with_semaphore(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(ConversionResult(
                        request_id=requests[i].request_id,
                        success=False,
                        error_details=str(result)
                    ))
                else:
                    final_results.append(result)
                    
            return final_results
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {e}")
            return [
                ConversionResult(
                    request_id=req.request_id,
                    success=False,
                    error_details=str(e)
                ) for req in requests
            ]
            
    async def get_supported_conversions(self) -> Dict[str, List[str]]:
        """Get supported format conversions"""        return self.conversion_matrix
        
    async def estimate_conversion_time(self, source_file: str, target_format: str) -> Dict[str, Any]:
        """Estimate conversion time and resources"""        try:
            # Get file information
            file_size = os.path.getsize(source_file)
            source_format = await self.format_detector.detect_format(source_file)
            
            # Get historical performance data
            format_key = f"{source_format}_to_{target_format}"
            avg_time = self.conversion_stats["formats_converted"].get(format_key, {}).get("avg_time", 30.0)
            
            # Estimate based on file size and historical data
            size_factor = file_size / (1024 * 1024)  # MB
            estimated_time = avg_time * (size_factor / 10)  # Rough estimation
            
            return {
                "estimated_time_seconds": estimated_time,
                "file_size_mb": size_factor,
                "source_format": source_format,
                "target_format": target_format,
                "confidence": 0.7 if format_key in self.conversion_stats["formats_converted"] else 0.3
            }
            
        except Exception as e:
            logger.error(f"Failed to estimate conversion time: {e}")
            return {
                "estimated_time_seconds": 60.0,
                "confidence": 0.1,
                "error": str(e)
            }
            
    def create_custom_profile(self, profile: ConversionProfile) -> bool:
        """Create custom conversion profile"""        try:
            # Validate profile
            if not self._validate_conversion_profile(profile):
                return False
                
            self.profiles[profile.profile_id] = profile
            logger.info(f"Custom profile created: {profile.profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom profile: {e}")
            return False
            
    def get_conversion_profiles(self, source_format: str = None, target_format: str = None) -> List[ConversionProfile]:
        """Get available conversion profiles"""        profiles = list(self.profiles.values())
        
        if source_format:
            profiles = [p for p in profiles if source_format in p.source_formats]
            
        if target_format:
            profiles = [p for p in profiles if p.target_format == target_format]
            
        return profiles
        
    async def optimize_for_platform(self, source_file: str, platform: str) -> ConversionResult:
        """Optimize file for specific platform"""        platform_configs = {
            "youtube": {
                "target_format": "mp4",
                "quality": ConversionQuality.HIGH,
                "parameters": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "resolution": "1920x1080",
                    "bitrate": "8000k"
                }
            },
            "instagram": {
                "target_format": "mp4",
                "quality": ConversionQuality.MEDIUM,
                "parameters": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "resolution": "1080x1080",
                    "bitrate": "3500k"
                }
            },
            "tiktok": {
                "target_format": "mp4",
                "quality": ConversionQuality.MEDIUM,
                "parameters": {
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "resolution": "1080x1920",
                    "bitrate": "2500k"
                }
            },
            "spotify": {
                "target_format": "mp3",
                "quality": ConversionQuality.HIGH,
                "parameters": {
                    "audio_codec": "mp3",
                    "bitrate": "320k",
                    "sample_rate": "44100"
                }
            }
        }
        
        config = platform_configs.get(platform.lower())
        if not config:
            raise ValueError(f"Platform {platform} not supported")
            
        request = ConversionRequest(
            request_id=f"platform_{platform}_{datetime.now().timestamp()}",
            source_file=source_file,
            target_format=config["target_format"],
            quality=config["quality"],
            custom_parameters=config["parameters"]
        )
        
        return await self.convert_file(request)
        
    async def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""        return {
            **self.conversion_stats,
            "total_profiles": len(self.profiles),
            "supported_formats": len(self.conversion_matrix),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Converter health check"""        try:
            # Check external tools
            tools_status = await self._check_external_tools()
            
            # Check temp directory
            temp_writable = os.access(self.temp_directory, os.W_OK)
            
            # Check component health
            component_health = {
                "format_detector": await self.format_detector.health_check(),
                "metadata_extractor": await self.metadata_extractor.health_check(),
                "quality_analyzer": await self.quality_analyzer.health_check()
            }
            
            status = "healthy"
            if not all(tools_status.values()) or not temp_writable:
                status = "degraded"
                
            unhealthy_components = [
                name for name, health in component_health.items()
                if health.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                status = "degraded"
                
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "external_tools": tools_status,
                "temp_directory_writable": temp_writable,
                "components": component_health,
                "conversion_stats": self.conversion_stats
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _perform_conversion(
        self, 
        request: ConversionRequest, 
        profile: ConversionProfile,
        source_metadata: Dict[str, Any]
    ) -> ConversionResult:
        """Perform actual file conversion"""        try:
            # Generate output path if not provided
            if not request.output_path:
                source_path = Path(request.source_file)
                output_filename = f"{source_path.stem}.{request.target_format}"
                request.output_path = os.path.join(self.temp_directory, output_filename)
                
            # Get file sizes
            original_size = os.path.getsize(request.source_file)
            
            # Determine conversion method based on format
            conversion_method = self._get_conversion_method(profile.target_format)
            
            # Perform conversion
            start_time = datetime.now()
            await conversion_method(request, profile, source_metadata)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Verify output file
            if not os.path.exists(request.output_path):
                raise RuntimeError("Conversion completed but output file not found")
                
            # Get converted file size
            converted_size = os.path.getsize(request.output_path)
            compression_ratio = converted_size / original_size if original_size > 0 else 1.0
            
            # Extract converted file metadata
            converted_metadata = await self.metadata_extractor.extract_metadata(request.output_path)
            
            # Generate quality metrics
            quality_metrics = await self.quality_analyzer.compare_quality(
                request.source_file, request.output_path
            )
            
            # Generate thumbnails if requested
            thumbnails = []
            if request.thumbnail_generation:
                thumbnails = await self._generate_thumbnails(request.output_path)
                
            return ConversionResult(
                request_id=request.request_id,
                success=True,
                output_file=request.output_path,
                original_format=source_metadata.get("format"),
                target_format=request.target_format,
                file_size_original=original_size,
                file_size_converted=converted_size,
                compression_ratio=compression_ratio,
                processing_time=processing_time,
                quality_metrics=quality_metrics,
                metadata=converted_metadata,
                thumbnails=thumbnails
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
            
    async def _convert_video(self, request: ConversionRequest, profile: ConversionProfile, metadata: Dict[str, Any]):
        """Convert video file using FFmpeg"""        try:
            # Build FFmpeg command
            input_stream = ffmpeg.input(request.source_file)
            
            # Apply preprocessing filters
            for filter_name in profile.preprocessing:
                input_stream = self._apply_video_filter(input_stream, filter_name, profile.parameters)
                
            # Set codec and quality parameters
            codec_params = profile.codec_settings.copy()
            codec_params.update(request.custom_parameters)
            
            # Configure output
            output_stream = ffmpeg.output(input_stream, request.output_path, **codec_params)
            
            # Run conversion with progress callback
            if request.progress_callback:
                await self._run_ffmpeg_with_progress(output_stream, request.progress_callback)
            else:
                ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
                
        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            raise
            
    async def _convert_audio(self, request: ConversionRequest, profile: ConversionProfile, metadata: Dict[str, Any]):
        """Convert audio file using FFmpeg"""        try:
            # Build FFmpeg command for audio
            input_stream = ffmpeg.input(request.source_file)
            
            # Apply audio filters
            for filter_name in profile.preprocessing:
                input_stream = self._apply_audio_filter(input_stream, filter_name, profile.parameters)
                
            # Set audio codec and quality
            audio_params = profile.codec_settings.copy()
            audio_params.update(request.custom_parameters)
            
            # Configure output
            output_stream = ffmpeg.output(input_stream, request.output_path, **audio_params)
            
            # Run conversion
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise
            
    async def _convert_image(self, request: ConversionRequest, profile: ConversionProfile, metadata: Dict[str, Any]):
        """Convert image file using PIL"""        try:
            # Open image
            with Image.open(request.source_file) as img:
                # Apply preprocessing
                for filter_name in profile.preprocessing:
                    img = self._apply_image_filter(img, filter_name, profile.parameters)
                    
                # Set quality parameters
                save_params = profile.output_settings.copy()
                save_params.update(request.custom_parameters)
                
                # Handle format-specific parameters
                if request.target_format.lower() == 'jpeg':
                    save_params.setdefault('quality', 85)
                    save_params.setdefault('optimize', True)
                elif request.target_format.lower() == 'png':
                    save_params.setdefault('optimize', True)
                elif request.target_format.lower() == 'webp':
                    save_params.setdefault('quality', 80)
                    save_params.setdefault('method', 6)
                    
                # Convert and save
                if img.mode in ('RGBA', 'LA') and request.target_format.lower() in ('jpeg', 'jpg'):
                    # Convert to RGB for JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                    
                img.save(request.output_path, format=request.target_format.upper(), **save_params)
                
        except Exception as e:
            logger.error(f"Image conversion failed: {e}")
            raise
            
    async def _convert_document(self, request: ConversionRequest, profile: ConversionProfile, metadata: Dict[str, Any]):
        """Convert document file using Pandoc"""        try:
            # Use Pandoc for document conversion
            output = pypandoc.convert_file(
                request.source_file,
                request.target_format,
                outputfile=request.output_path,
                extra_args=profile.parameters.get("pandoc_args", [])
            )
            
        except Exception as e:
            logger.error(f"Document conversion failed: {e}")
            raise
            
    def _get_conversion_method(self, target_format: str):
        """Get appropriate conversion method based on target format"""        video_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
        audio_formats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        image_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
        document_formats = ['pdf', 'docx', 'html', 'txt', 'md']
        
        target_format = target_format.lower()
        
        if target_format in video_formats:
            return self._convert_video
        elif target_format in audio_formats:
            return self._convert_audio
        elif target_format in image_formats:
            return self._convert_image
        elif target_format in document_formats:
            return self._convert_document
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
            
    def _apply_video_filter(self, stream, filter_name: str, parameters: Dict[str, Any]):
        """Apply video filter to FFmpeg stream"""        if filter_name == "scale":
            width = parameters.get("width", 1920)
            height = parameters.get("height", 1080)
            return stream.video.filter('scale', width, height)
        elif filter_name == "fps":
            fps = parameters.get("fps", 30)
            return stream.video.filter('fps', fps)
        elif filter_name == "crop":
            x = parameters.get("x", 0)
            y = parameters.get("y", 0)
            width = parameters.get("crop_width", 1920)
            height = parameters.get("crop_height", 1080)
            return stream.video.filter('crop', width, height, x, y)
        else:
            return stream
            
    def _apply_audio_filter(self, stream, filter_name: str, parameters: Dict[str, Any]):
        """Apply audio filter to FFmpeg stream"""        if filter_name == "volume":
            volume = parameters.get("volume", 1.0)
            return stream.audio.filter('volume', volume)
        elif filter_name == "normalize":
            return stream.audio.filter('loudnorm')
        elif filter_name == "highpass":
            frequency = parameters.get("frequency", 100)
            return stream.audio.filter('highpass', f=frequency)
        elif filter_name == "lowpass":
            frequency = parameters.get("frequency", 8000)
            return stream.audio.filter('lowpass', f=frequency)
        else:
            return stream
            
    def _apply_image_filter(self, image: Image.Image, filter_name: str, parameters: Dict[str, Any]) -> Image.Image:
        """Apply image filter using PIL"""        if filter_name == "resize":
            width = parameters.get("width", image.width)
            height = parameters.get("height", image.height)
            return image.resize((width, height), Image.Resampling.LANCZOS)
        elif filter_name == "crop":
            left = parameters.get("left", 0)
            top = parameters.get("top", 0)
            right = parameters.get("right", image.width)
            bottom = parameters.get("bottom", image.height)
            return image.crop((left, top, right, bottom))
        elif filter_name == "rotate":
            angle = parameters.get("angle", 0)
            return image.rotate(angle, expand=True)
        elif filter_name == "autocontrast":
            return ImageOps.autocontrast(image)
        else:
            return image
            
    async def _run_ffmpeg_with_progress(self, output_stream, progress_callback):
        """Run FFmpeg with progress tracking"""        # This is a simplified implementation
        # In production, you would parse FFmpeg progress output
        process = ffmpeg.run_async(output_stream, pipe_stderr=True)
        
        while True:
            output = process.stderr.readline()
            if not output:
                break
                
            # Parse progress from FFmpeg output
            # This is a placeholder - actual implementation would parse time/duration
            if progress_callback:
                await progress_callback(50.0)  # Placeholder progress
                
        process.wait()
        
    def _create_default_profiles(self) -> Dict[str, ConversionProfile]:
        """Create default conversion profiles"""        profiles = {}
        
        # Video profiles
        profiles["video_high_quality"] = ConversionProfile(
            profile_id="video_high_quality",
            name="High Quality Video",
            description="High quality video conversion",
            source_formats=["avi", "mov", "mkv", "webm"],
            target_format="mp4",
            quality=ConversionQuality.HIGH,
            mode=ConversionMode.QUALITY,
            codec_settings={
                "vcodec": "libx264",
                "acodec": "aac",
                "preset": "medium",
                "crf": 20
            }
        )
        
        # Audio profiles
        profiles["audio_high_quality"] = ConversionProfile(
            profile_id="audio_high_quality",
            name="High Quality Audio",
            description="High quality audio conversion",
            source_formats=["wav", "flac", "aac", "ogg"],
            target_format="mp3",
            quality=ConversionQuality.HIGH,
            mode=ConversionMode.QUALITY,
            codec_settings={
                "acodec": "libmp3lame",
                "audio_bitrate": "320k"
            }
        )
        
        # Image profiles
        profiles["image_web_optimized"] = ConversionProfile(
            profile_id="image_web_optimized",
            name="Web Optimized Image",
            description="Optimized for web delivery",
            source_formats=["png", "bmp", "tiff"],
            target_format="jpg",
            quality=ConversionQuality.MEDIUM,
            mode=ConversionMode.FAST,
            output_settings={
                "quality": 85,
                "optimize": True
            }
        )
        
        return profiles
        
    def _build_conversion_matrix(self) -> Dict[str, List[str]]:
        """Build supported conversion matrix"""        return {
            # Video formats
            "mp4": ["avi", "mov", "mkv", "webm", "flv"],
            "avi": ["mp4", "mov", "mkv", "webm"],
            "mov": ["mp4", "avi", "mkv", "webm"],
            "mkv": ["mp4", "avi", "mov", "webm"],
            "webm": ["mp4", "avi", "mov", "mkv"],
            
            # Audio formats
            "mp3": ["wav", "flac", "aac", "ogg", "m4a"],
            "wav": ["mp3", "flac", "aac", "ogg"],
            "flac": ["mp3", "wav", "aac", "ogg"],
            "aac": ["mp3", "wav", "flac", "ogg"],
            "ogg": ["mp3", "wav", "flac", "aac"],
            
            # Image formats
            "jpg": ["png", "gif", "bmp", "tiff", "webp"],
            "png": ["jpg", "gif", "bmp", "tiff", "webp"],
            "gif": ["jpg", "png", "bmp", "tiff"],
            "webp": ["jpg", "png", "gif", "bmp", "tiff"],
            "bmp": ["jpg", "png", "gif", "tiff"],
            "tiff": ["jpg", "png", "gif", "bmp"],
            
            # Document formats
            "pdf": ["docx", "html", "txt", "md"],
            "docx": ["pdf", "html", "txt", "md"],
            "html": ["pdf", "docx", "txt", "md"],
            "txt": ["pdf", "docx", "html", "md"],
            "md": ["pdf", "docx", "html", "txt"]
        }
        
    def _is_conversion_supported(self, source_format: str, target_format: str) -> bool:
        """Check if conversion is supported"""        return target_format.lower() in self.conversion_matrix.get(source_format.lower(), [])
        
    async def _select_optimal_profile(self, source_format: str, target_format: str, quality: ConversionQuality) -> ConversionProfile:
        """Select optimal conversion profile"""        # Find matching profiles
        matching_profiles = [
            profile for profile in self.profiles.values()
            if (source_format in profile.source_formats and 
                profile.target_format == target_format and
                profile.quality == quality)
        ]
        
        if matching_profiles:
            return matching_profiles[0]
            
        # Create default profile
        return ConversionProfile(
            profile_id=f"default_{source_format}_to_{target_format}",
            name=f"Default {source_format} to {target_format}",
            description="Auto-generated default profile",
            source_formats=[source_format],
            target_format=target_format,
            quality=quality,
            mode=ConversionMode.BALANCED
        )
        
    async def _validate_conversion_request(self, request: ConversionRequest) -> Dict[str, Any]:
        """Validate conversion request"""        try:
            # Check source file exists
            if not os.path.exists(request.source_file):
                return {"valid": False, "error": "Source file not found"}
                
            # Check file size
            file_size = os.path.getsize(request.source_file)
            if file_size > self.max_file_size:
                return {"valid": False, "error": "File size exceeds maximum limit"}
                
            # Check temp directory
            if not os.access(self.temp_directory, os.W_OK):
                return {"valid": False, "error": "Temporary directory not writable"}
                
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
            
    def _validate_conversion_profile(self, profile: ConversionProfile) -> bool:
        """Validate conversion profile"""        try:
            # Basic validation
            if not profile.profile_id or not profile.name:
                return False
                
            if not profile.source_formats or not profile.target_format:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Profile validation error: {e}")
            return False
            
    async def _load_conversion_profiles(self):
        """Load conversion profiles"""        # Load default profiles
        self.profiles.update(self.default_profiles)
        
        # Load custom profiles from configuration
        custom_profiles = self.config.get("custom_profiles", [])
        for profile_config in custom_profiles:
            try:
                profile = ConversionProfile(**profile_config)
                if self._validate_conversion_profile(profile):
                    self.profiles[profile.profile_id] = profile
            except Exception as e:
                logger.error(f"Failed to load custom profile: {e}")
                
    async def _verify_external_tools(self):
        """Verify external tools availability"""        tools = ["ffmpeg", "ffprobe"]
        
        for tool in tools:
            try:
                result = subprocess.run([tool, "-version"], capture_output=True, timeout=10)
                if result.returncode != 0:
                    logger.warning(f"External tool {tool} not available")
            except Exception as e:
                logger.warning(f"Failed to verify tool {tool}: {e}")
                
    async def _check_external_tools(self) -> Dict[str, bool]:
        """Check external tools status"""        tools_status = {}
        tools = ["ffmpeg", "ffprobe", "pandoc"]
        
        for tool in tools:
            try:
                result = subprocess.run([tool, "-version"], capture_output=True, timeout=5)
                tools_status[tool] = result.returncode == 0
            except Exception:
                tools_status[tool] = False
                
        return tools_status
        
    async def _generate_thumbnails(self, video_file: str) -> List[str]:
        """Generate thumbnail images from video"""        try:
            thumbnails = []
            # This is a simplified implementation
            # In production, you would generate multiple thumbnails at different timestamps
            
            thumbnail_path = video_file.replace('.mp4', '_thumb.jpg')
            
            # Use FFmpeg to extract thumbnail
            (
                ffmpeg
                .input(video_file, ss=30)  # Extract frame at 30 seconds
                .output(thumbnail_path, vframes=1)
                .run(overwrite_output=True, quiet=True)
            )
            
            if os.path.exists(thumbnail_path):
                thumbnails.append(thumbnail_path)
                
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return []
            
    async def _update_conversion_stats(self, source_format: str, target_format: str, processing_time: float, success: bool):
        """Update conversion statistics"""        self.conversion_stats["total_conversions"] += 1
        
        if success:
            self.conversion_stats["successful_conversions"] += 1
        else:
            self.conversion_stats["failed_conversions"] += 1
            
        # Update processing time
        total_time = self.conversion_stats["total_processing_time"] + processing_time
        self.conversion_stats["total_processing_time"] = total_time
        self.conversion_stats["average_processing_time"] = total_time / self.conversion_stats["total_conversions"]
        
        # Update format-specific stats
        format_key = f"{source_format}_to_{target_format}"
        if format_key not in self.conversion_stats["formats_converted"]:
            self.conversion_stats["formats_converted"][format_key] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }
            
        format_stats = self.conversion_stats["formats_converted"][format_key]
        format_stats["count"] += 1
        format_stats["total_time"] += processing_time
        format_stats["avg_time"] = format_stats["total_time"] / format_stats["count"]
