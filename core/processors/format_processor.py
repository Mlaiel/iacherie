"""Format Processor Module - IA-Influencer-Agent Platform

Industrial-grade format conversion and optimization engine for content creators.
Comprehensive format handling, transcoding, and optimization for all content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""
import asyncio
import logging
import json
import time
import uuid
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import os

# Format conversion imports
try:
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter
    import pillow_heif  # For HEIF/HEIC support
    IMAGE_CONVERSION_AVAILABLE = True
except ImportError:
    IMAGE_CONVERSION_AVAILABLE = False

try:
    import ffmpeg
    import moviepy.editor as mp
    VIDEO_CONVERSION_AVAILABLE = True
except ImportError:
    VIDEO_CONVERSION_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    AUDIO_CONVERSION_AVAILABLE = True
except ImportError:
    AUDIO_CONVERSION_AVAILABLE = False

try:
    import pypandoc
    import markdown
    from docx import Document
    from docx2txt import process as docx2txt_process
    from PyPDF2 import PdfReader, PdfWriter
    import openpyxl
    DOCUMENT_CONVERSION_AVAILABLE = True
except ImportError:
    DOCUMENT_CONVERSION_AVAILABLE = False

# Optimization libraries
try:
    from optimize_images import optimize_image
    import imageio
    OPTIMIZATION_LIBS_AVAILABLE = True
except ImportError:
    OPTIMIZATION_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class InputFormat(str, Enum):
    """Supported input formats"""
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"
    HEIC = "heic"
    RAW = "raw"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    M4V = "m4v"
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    WMA = "wma"
    M4A = "m4a"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    XLSX = "xlsx"
    XLS = "xls"
    PPTX = "pptx"
    PPT = "ppt"
    TXT = "txt"
    RTF = "rtf"
    HTML = "html"
    MARKDOWN = "markdown"


class OutputFormat(str, Enum):
    """Supported output formats"""
    # Optimized web formats
    WEBP = "webp"
    AVIF = "avif"
    WEBM = "webm"
    MP4_H264 = "mp4_h264"
    MP4_H265 = "mp4_h265"
    
    # Standard formats
    JPEG = "jpeg"
    PNG = "png"
    MP4 = "mp4"
    MP3 = "mp3"
    WAV = "wav"
    PDF = "pdf"
    
    # Platform-specific formats
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_POST = "instagram_post"
    TIKTOK_VIDEO = "tiktok_video"
    YOUTUBE_VIDEO = "youtube_video"
    TWITTER_VIDEO = "twitter_video"
    LINKEDIN_POST = "linkedin_post"


class QualityLevel(str, Enum):
    """Quality levels for conversion"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"
    CUSTOM = "custom"


class OptimizationTarget(str, Enum):
    """Optimization targets"""
    WEB = "web"
    MOBILE = "mobile"
    PRINT = "print"
    STREAMING = "streaming"
    ARCHIVE = "archive"
    SOCIAL_MEDIA = "social_media"


@dataclass
class FormatProcessingConfig:
    """Configuration for format processing"""
    # Quality settings
    default_quality_level: QualityLevel = QualityLevel.HIGH
    preserve_metadata: bool = True
    enable_progressive_encoding: bool = True
    
    # Optimization settings
    enable_auto_optimization: bool = True
    optimization_target: OptimizationTarget = OptimizationTarget.WEB
    enable_size_optimization: bool = True
    enable_quality_optimization: bool = True
    
    # Image settings
    image_max_width: int = 2048
    image_max_height: int = 2048
    jpeg_quality: int = 85
    png_compression: int = 6
    webp_quality: int = 85
    
    # Video settings
    video_max_width: int = 1920
    video_max_height: int = 1080
    video_bitrate: int = 2000  # kbps
    video_fps: int = 30
    enable_hardware_acceleration: bool = True
    
    # Audio settings
    audio_bitrate: int = 128  # kbps
    audio_sample_rate: int = 44100
    audio_channels: int = 2
    
    # Processing settings
    max_processing_time: int = 600  # 10 minutes
    enable_parallel_processing: bool = True
    temp_directory: Optional[str] = None
    cleanup_temp_files: bool = True
    
    # Platform-specific settings
    platform_presets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Advanced settings
    enable_ai_enhancement: bool = False
    enable_format_validation: bool = True
    enable_progress_tracking: bool = True


@dataclass
class ConversionJob:
    """Format conversion job"""
    job_id: str
    input_format: InputFormat
    output_format: OutputFormat
    input_path: str
    output_path: Optional[str] = None
    
    # Processing settings
    quality_level: QualityLevel = QualityLevel.HIGH
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Status and progress
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    output_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Metadata
    creator_id: Optional[str] = None
    original_metadata: Dict[str, Any] = field(default_factory=dict)
    output_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormatCapabilities:
    """Format capabilities and constraints"""
    format_name: str
    supported_codecs: List[str] = field(default_factory=list)
    max_resolution: Optional[Tuple[int, int]] = None
    max_duration: Optional[float] = None
    max_file_size: Optional[int] = None
    supports_transparency: bool = False
    supports_animation: bool = False
    supports_metadata: bool = True
    lossless_compression: bool = False
    platform_compatibility: List[str] = field(default_factory=list)


class FormatProcessor:
    """
    🔄 ENTERPRISE FORMAT PROCESSOR
    
    Industrial-grade format conversion and optimization engine with
    comprehensive support for all content types and platform-specific optimization.
    """
    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[FormatProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or FormatProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.FormatProcessor")
        
        # Format capabilities
        self._format_capabilities = {}
        
        # Active conversion jobs
        self._active_jobs: Dict[str, ConversionJob] = {}
        
        # Conversion statistics
        self._stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "total_size_saved": 0,
            "average_compression_ratio": 0.0
        }
        
        # Platform presets
        self._platform_presets = {
            "instagram_story": {
                "resolution": (1080, 1920),
                "duration": 15,
                "format": "mp4",
                "aspect_ratio": "9:16"
            },
            "instagram_post": {
                "resolution": (1080, 1080),
                "format": "jpeg",
                "aspect_ratio": "1:1"
            },
            "tiktok_video": {
                "resolution": (1080, 1920),
                "duration": 60,
                "format": "mp4",
                "aspect_ratio": "9:16"
            },
            "youtube_video": {
                "resolution": (1920, 1080),
                "format": "mp4",
                "aspect_ratio": "16:9"
            }
        }
        
        self._initialized = False
        
        # Log library availability
        if not IMAGE_CONVERSION_AVAILABLE:
            self.logger.warning("Image conversion libraries not available")
        
        if not VIDEO_CONVERSION_AVAILABLE:
            self.logger.warning("Video conversion libraries not available")
        
        if not AUDIO_CONVERSION_AVAILABLE:
            self.logger.warning("Audio conversion libraries not available")
        
        if not DOCUMENT_CONVERSION_AVAILABLE:
            self.logger.warning("Document conversion libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the format processor"""
        try:
            # Load format capabilities
            await self._load_format_capabilities()
            
            # Initialize platform presets
            self.config.platform_presets.update(self._platform_presets)
            
            # Create temp directory if needed
            if not self.config.temp_directory:
                self.config.temp_directory = tempfile.mkdtemp()
            
            self._initialized = True
            self.logger.info("✅ Format processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize format processor: {e}")
            return False
    
    async def convert_format(
        self,
        input_content: Union[str, bytes, Path],
        input_format: InputFormat,
        output_format: OutputFormat,
        quality_level: QualityLevel = QualityLevel.HIGH,
        custom_settings: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert content from one format to another
        
        Args:
            input_content: Input content (file path or bytes)
            input_format: Input format
            output_format: Desired output format
            quality_level: Quality level for conversion
            custom_settings: Custom conversion settings
            output_path: Optional output file path
            
        Returns:
            Conversion result
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            start_time = time.time()
            
            # Create conversion job
            job = ConversionJob(
                job_id=str(uuid.uuid4()),
                input_format=input_format,
                output_format=output_format,
                input_path=str(input_content) if not isinstance(input_content, bytes) else "bytes",
                output_path=output_path,
                quality_level=quality_level,
                custom_settings=custom_settings or {}
            )
            
            job.started_at = datetime.now()
            job.status = "processing"
            self._active_jobs[job.job_id] = job
            
            # Validate input format
            validation_result = await self._validate_input(input_content, input_format)
            if not validation_result["valid"]:
                job.status = "failed"
                job.error_message = validation_result["error"]
                return {
                    "success": False,
                    "job_id": job.job_id,
                    "error_message": validation_result["error"]
                }
            
            # Prepare input file
            input_file_path = await self._prepare_input_file(input_content, input_format)
            
            # Determine conversion method
            conversion_method = await self._get_conversion_method(input_format, output_format)
            
            # Perform conversion
            output_file_path = await conversion_method(
                input_file_path, job, output_path
            )
            
            # Validate output
            if not os.path.exists(output_file_path):
                raise Exception("Output file was not created")
            
            # Calculate metrics
            await self._calculate_conversion_metrics(job, input_file_path, output_file_path)
            
            # Finalize job
            job.status = "completed"
            job.completed_at = datetime.now()
            job.processing_time = time.time() - start_time
            job.output_path = output_file_path
            
            # Update statistics
            self._update_conversion_stats(job)
            
            # Cleanup temp files if needed
            if self.config.cleanup_temp_files and input_file_path != str(input_content):
                try:
                    os.unlink(input_file_path)
                except:
                    pass
            
            return {
                "success": True,
                "job_id": job.job_id,
                "output_path": output_file_path,
                "output_size": job.output_size,
                "compression_ratio": job.compression_ratio,
                "quality_metrics": job.quality_metrics,
                "processing_time": job.processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            
            if 'job' in locals():
                job.status = "failed"
                job.error_message = str(e)
                job.processing_time = time.time() - start_time
                self._stats["failed_conversions"] += 1
            
            return {
                "success": False,
                "job_id": job.job_id if 'job' in locals() else None,
                "error_message": str(e),
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def optimize_for_platform(
        self,
        input_content: Union[str, bytes, Path],
        platform: str,
        content_type: str = "auto",
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize content for specific platform
        
        Args:
            input_content: Input content
            platform: Target platform (instagram, tiktok, youtube, etc.)
            content_type: Type of content (image, video, audio)
            custom_settings: Custom optimization settings
            
        Returns:
            Optimization result
        """
        try:
            # Get platform preset
            preset = self.config.platform_presets.get(platform)
            if not preset:
                return {
                    "success": False,
                    "error_message": f"Platform '{platform}' not supported"
                }
            
            # Detect input format
            input_format = await self._detect_input_format(input_content)
            
            # Determine output format based on platform and content type
            output_format = await self._determine_platform_output_format(
                platform, content_type, input_format
            )
            
            # Merge platform settings with custom settings
            optimization_settings = {**preset, **(custom_settings or {})}
            
            # Perform conversion with platform optimization
            result = await self.convert_format(
                input_content=input_content,
                input_format=input_format,
                output_format=output_format,
                quality_level=QualityLevel.HIGH,
                custom_settings=optimization_settings
            )
            
            if result["success"]:
                result["platform"] = platform
                result["optimization_applied"] = True
                result["platform_settings"] = optimization_settings
            
            return result
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def batch_convert(
        self,
        input_files: List[Dict[str, Any]],
        output_format: OutputFormat,
        quality_level: QualityLevel = QualityLevel.HIGH,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert multiple files in batch
        
        Args:
            input_files: List of input file definitions
            output_format: Target output format
            quality_level: Quality level for conversion
            custom_settings: Custom conversion settings
            
        Returns:
            Batch conversion results
        """
        try:
            batch_id = str(uuid.uuid4())
            batch_results = []
            successful_conversions = 0
            failed_conversions = 0
            
            # Process files
            if self.config.enable_parallel_processing:
                # Parallel processing
                tasks = []
                for file_info in input_files:
                    task = self.convert_format(
                        input_content=file_info["path"],
                        input_format=InputFormat(file_info["format"]),
                        output_format=output_format,
                        quality_level=quality_level,
                        custom_settings=custom_settings,
                        output_path=file_info.get("output_path")
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        batch_results.append({
                            "input_file": input_files[i]["path"],
                            "success": False,
                            "error_message": str(result)
                        })
                        failed_conversions += 1
                    else:
                        batch_results.append({
                            "input_file": input_files[i]["path"],
                            **result
                        })
                        if result["success"]:
                            successful_conversions += 1
                        else:
                            failed_conversions += 1
            else:
                # Sequential processing
                for file_info in input_files:
                    result = await self.convert_format(
                        input_content=file_info["path"],
                        input_format=InputFormat(file_info["format"]),
                        output_format=output_format,
                        quality_level=quality_level,
                        custom_settings=custom_settings,
                        output_path=file_info.get("output_path")
                    )
                    
                    batch_results.append({
                        "input_file": file_info["path"],
                        **result
                    })
                    
                    if result["success"]:
                        successful_conversions += 1
                    else:
                        failed_conversions += 1
            
            return {
                "success": True,
                "batch_id": batch_id,
                "total_files": len(input_files),
                "successful_conversions": successful_conversions,
                "failed_conversions": failed_conversions,
                "results": batch_results
            }
            
        except Exception as e:
            self.logger.error(f"Batch conversion failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """Get information about a specific format"""
        try:
            capabilities = self._format_capabilities.get(format_name)
            if not capabilities:
                return {
                    "success": False,
                    "error_message": f"Format '{format_name}' not supported"
                }
            
            return {
                "success": True,
                "format_info": capabilities.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Format info retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_supported_conversions(self) -> Dict[str, Any]:
        """Get list of supported format conversions"""
        try:
            conversions = {}
            
            # Image conversions
            if IMAGE_CONVERSION_AVAILABLE:
                image_inputs = [InputFormat.JPEG, InputFormat.PNG, InputFormat.GIF, InputFormat.WEBP]
                image_outputs = [OutputFormat.JPEG, OutputFormat.PNG, OutputFormat.WEBP]
                conversions["image"] = {
                    "inputs": [f.value for f in image_inputs],
                    "outputs": [f.value for f in image_outputs]
                }
            
            # Video conversions
            if VIDEO_CONVERSION_AVAILABLE:
                video_inputs = [InputFormat.MP4, InputFormat.AVI, InputFormat.MOV, InputFormat.WEBM]
                video_outputs = [OutputFormat.MP4, OutputFormat.WEBM, OutputFormat.MP4_H264]
                conversions["video"] = {
                    "inputs": [f.value for f in video_inputs],
                    "outputs": [f.value for f in video_outputs]
                }
            
            # Audio conversions
            if AUDIO_CONVERSION_AVAILABLE:
                audio_inputs = [InputFormat.MP3, InputFormat.WAV, InputFormat.FLAC]
                audio_outputs = [OutputFormat.MP3, OutputFormat.WAV]
                conversions["audio"] = {
                    "inputs": [f.value for f in audio_inputs],
                    "outputs": [f.value for f in audio_outputs]
                }
            
            return {
                "success": True,
                "supported_conversions": conversions
            }
            
        except Exception as e:
            self.logger.error(f"Supported conversions retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _validate_input(
        self,
        input_content: Union[str, bytes, Path],
        input_format: InputFormat
    ) -> Dict[str, Any]:
        """Validate input content and format"""
        try:
            # Basic validation
            if isinstance(input_content, (str, Path)):
                file_path = Path(input_content)
                if not file_path.exists():
                    return {
                        "valid": False,
                        "error": "Input file does not exist"
                    }
                
                if file_path.stat().st_size == 0:
                    return {
                        "valid": False,
                        "error": "Input file is empty"
                    }
            
            elif isinstance(input_content, bytes):
                if len(input_content) == 0:
                    return {
                        "valid": False,
                        "error": "Input content is empty"
                    }
            
            # Format-specific validation would be implemented here
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _prepare_input_file(
        self,
        input_content: Union[str, bytes, Path],
        input_format: InputFormat
    ) -> str:
        """Prepare input file for processing"""
        try:
            if isinstance(input_content, bytes):
                # Save bytes to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=f".{input_format.value}",
                    dir=self.config.temp_directory
                )
                temp_file.write(input_content)
                temp_file.close()
                return temp_file.name
            else:
                return str(input_content)
                
        except Exception as e:
            self.logger.error(f"Input file preparation failed: {e}")
            raise
    
    async def _get_conversion_method(
        self,
        input_format: InputFormat,
        output_format: OutputFormat
    ) -> callable:
        """Get appropriate conversion method"""
        try:
            # Image conversions
            if (input_format in [InputFormat.JPEG, InputFormat.PNG, InputFormat.GIF, InputFormat.WEBP] and
                output_format in [OutputFormat.JPEG, OutputFormat.PNG, OutputFormat.WEBP]):
                return self._convert_image
            
            # Video conversions
            elif (input_format in [InputFormat.MP4, InputFormat.AVI, InputFormat.MOV, InputFormat.WEBM] and
                  output_format in [OutputFormat.MP4, OutputFormat.WEBM, OutputFormat.MP4_H264]):
                return self._convert_video
            
            # Audio conversions
            elif (input_format in [InputFormat.MP3, InputFormat.WAV, InputFormat.FLAC] and
                  output_format in [OutputFormat.MP3, OutputFormat.WAV]):
                return self._convert_audio
            
            # Document conversions
            elif input_format in [InputFormat.PDF, InputFormat.DOCX, InputFormat.TXT]:
                return self._convert_document
            
            else:
                raise Exception(f"Conversion from {input_format} to {output_format} not supported")
                
        except Exception as e:
            self.logger.error(f"Conversion method selection failed: {e}")
            raise
    
    async def _convert_image(
        self,
        input_path: str,
        job: ConversionJob,
        output_path: Optional[str] = None
    ) -> str:
        """Convert image format"""
        try:
            if not IMAGE_CONVERSION_AVAILABLE:
                raise Exception("Image conversion libraries not available")
            
            # Generate output path if not provided
            if not output_path:
                output_ext = job.output_format.value
                output_path = os.path.join(
                    self.config.temp_directory,
                    f"{job.job_id}.{output_ext}"
                )
            
            # Open image
            with Image.open(input_path) as img:
                # Apply size constraints
                if img.width > self.config.image_max_width or img.height > self.config.image_max_height:
                    img.thumbnail((self.config.image_max_width, self.config.image_max_height), Image.Resampling.LANCZOS)
                
                # Apply quality settings
                save_kwargs = {}
                
                if job.output_format == OutputFormat.JPEG:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    save_kwargs["quality"] = job.custom_settings.get("quality", self.config.jpeg_quality)
                    save_kwargs["optimize"] = True
                    if self.config.enable_progressive_encoding:
                        save_kwargs["progressive"] = True
                
                elif job.output_format == OutputFormat.PNG:
                    save_kwargs["optimize"] = True
                    save_kwargs["compress_level"] = job.custom_settings.get("compression", self.config.png_compression)
                
                elif job.output_format == OutputFormat.WEBP:
                    save_kwargs["quality"] = job.custom_settings.get("quality", self.config.webp_quality)
                    save_kwargs["method"] = 6  # Best compression
                
                # Apply custom resize if specified
                if "resize" in job.custom_settings:
                    new_size = job.custom_settings["resize"]
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Apply enhancement if enabled
                if job.custom_settings.get("enhance", False):
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)
                
                # Save image
                img.save(output_path, format=job.output_format.value.upper(), **save_kwargs)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Image conversion failed: {e}")
            raise
    
    async def _convert_video(
        self,
        input_path: str,
        job: ConversionJob,
        output_path: Optional[str] = None
    ) -> str:
        """Convert video format"""
        try:
            if not VIDEO_CONVERSION_AVAILABLE:
                raise Exception("Video conversion libraries not available")
            
            # Generate output path if not provided
            if not output_path:
                output_ext = "mp4" if job.output_format in [OutputFormat.MP4, OutputFormat.MP4_H264] else job.output_format.value
                output_path = os.path.join(
                    self.config.temp_directory,
                    f"{job.job_id}.{output_ext}"
                )
            
            # Load video
            clip = mp.VideoFileClip(input_path)
            
            # Apply size constraints
            if clip.w > self.config.video_max_width or clip.h > self.config.video_max_height:
                scale_factor = min(
                    self.config.video_max_width / clip.w,
                    self.config.video_max_height / clip.h
                )
                new_width = int(clip.w * scale_factor)
                new_height = int(clip.h * scale_factor)
                clip = clip.resize((new_width, new_height))
            
            # Apply custom settings
            if "duration" in job.custom_settings:
                duration = job.custom_settings["duration"]
                clip = clip.subclip(0, min(duration, clip.duration))
            
            # Prepare codec settings
            codec = "libx264"
            if job.output_format == OutputFormat.MP4_H265:
                codec = "libx265"
            elif job.output_format == OutputFormat.WEBM:
                codec = "libvpx-vp9"
            
            # Write video
            clip.write_videofile(
                output_path,
                codec=codec,
                bitrate=f"{job.custom_settings.get('bitrate', self.config.video_bitrate)}k",
                fps=job.custom_settings.get("fps", self.config.video_fps),
                verbose=False,
                logger=None
            )
            
            clip.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Video conversion failed: {e}")
            raise
    
    async def _convert_audio(
        self,
        input_path: str,
        job: ConversionJob,
        output_path: Optional[str] = None
    ) -> str:
        """Convert audio format"""
        try:
            if not AUDIO_CONVERSION_AVAILABLE:
                raise Exception("Audio conversion libraries not available")
            
            # Generate output path if not provided
            if not output_path:
                output_ext = job.output_format.value
                output_path = os.path.join(
                    self.config.temp_directory,
                    f"{job.job_id}.{output_ext}"
                )
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Apply settings
            if job.output_format == OutputFormat.MP3:
                audio.export(
                    output_path,
                    format="mp3",
                    bitrate=f"{job.custom_settings.get('bitrate', self.config.audio_bitrate)}k"
                )
            elif job.output_format == OutputFormat.WAV:
                audio.export(
                    output_path,
                    format="wav"
                )
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            raise
    
    async def _convert_document(
        self,
        input_path: str,
        job: ConversionJob,
        output_path: Optional[str] = None
    ) -> str:
        """Convert document format"""
        try:
            if not DOCUMENT_CONVERSION_AVAILABLE:
                raise Exception("Document conversion libraries not available")
            
            # Generate output path if not provided
            if not output_path:
                output_ext = job.output_format.value
                output_path = os.path.join(
                    self.config.temp_directory,
                    f"{job.job_id}.{output_ext}"
                )
            
            # Document conversion would be implemented here
            # Using pypandoc, python-docx, etc.
            
            # For now, just copy the file
            shutil.copy2(input_path, output_path)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Document conversion failed: {e}")
            raise
    
    async def _detect_input_format(self, input_content: Union[str, bytes, Path]) -> InputFormat:
        """Detect input format from content"""
        try:
            if isinstance(input_content, (str, Path)):
                file_path = Path(input_content)
                ext = file_path.suffix.lower().lstrip('.')
                
                # Map extensions to formats
                format_map = {
                    'jpg': InputFormat.JPEG,
                    'jpeg': InputFormat.JPEG,
                    'png': InputFormat.PNG,
                    'gif': InputFormat.GIF,
                    'webp': InputFormat.WEBP,
                    'mp4': InputFormat.MP4,
                    'avi': InputFormat.AVI,
                    'mov': InputFormat.MOV,
                    'webm': InputFormat.WEBM,
                    'mp3': InputFormat.MP3,
                    'wav': InputFormat.WAV,
                    'flac': InputFormat.FLAC,
                    'pdf': InputFormat.PDF,
                    'docx': InputFormat.DOCX,
                    'txt': InputFormat.TXT
                }
                
                return format_map.get(ext, InputFormat.JPEG)  # Default
            
            # For bytes, would analyze file signature
            return InputFormat.JPEG  # Default
            
        except Exception as e:
            self.logger.error(f"Input format detection failed: {e}")
            return InputFormat.JPEG  # Default
    
    async def _determine_platform_output_format(
        self,
        platform: str,
        content_type: str,
        input_format: InputFormat
    ) -> OutputFormat:
        """Determine optimal output format for platform"""
        try:
            platform_formats = {
                "instagram": {
                    "image": OutputFormat.JPEG,
                    "video": OutputFormat.MP4,
                    "auto": OutputFormat.JPEG if "image" in input_format.value else OutputFormat.MP4
                },
                "tiktok": {
                    "video": OutputFormat.MP4,
                    "auto": OutputFormat.MP4
                },
                "youtube": {
                    "video": OutputFormat.MP4_H264,
                    "auto": OutputFormat.MP4_H264
                },
                "web": {
                    "image": OutputFormat.WEBP,
                    "video": OutputFormat.WEBM,
                    "auto": OutputFormat.WEBP if "image" in input_format.value else OutputFormat.WEBM
                }
            }
            
            platform_config = platform_formats.get(platform, {})
            return platform_config.get(content_type, platform_config.get("auto", OutputFormat.JPEG))
            
        except Exception as e:
            self.logger.error(f"Platform output format determination failed: {e}")
            return OutputFormat.JPEG  # Default
    
    async def _calculate_conversion_metrics(
        self,
        job: ConversionJob,
        input_path: str,
        output_path: str
    ):
        """Calculate conversion metrics"""
        try:
            # File sizes
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            
            job.output_size = output_size
            job.compression_ratio = input_size / output_size if output_size > 0 else 1.0
            
            # Quality metrics would be calculated here
            job.quality_metrics = {
                "size_reduction": 1.0 - (output_size / input_size) if input_size > 0 else 0.0,
                "compression_efficiency": job.compression_ratio
            }
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {e}")
    
    def _update_conversion_stats(self, job: ConversionJob):
        """Update conversion statistics"""
        try:
            self._stats["total_conversions"] += 1
            
            if job.status == "completed":
                self._stats["successful_conversions"] += 1
                
                if job.compression_ratio:
                    # Update average compression ratio
                    current_avg = self._stats["average_compression_ratio"]
                    total_successful = self._stats["successful_conversions"]
                    self._stats["average_compression_ratio"] = (
                        (current_avg * (total_successful - 1) + job.compression_ratio) / total_successful
                    )
                
                if job.output_size:
                    input_size = job.output_size * job.compression_ratio if job.compression_ratio else 0
                    size_saved = input_size - job.output_size
                    if size_saved > 0:
                        self._stats["total_size_saved"] += size_saved
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    async def _load_format_capabilities(self):
        """Load format capabilities information"""
        try:
            # Image format capabilities
            self._format_capabilities["jpeg"] = FormatCapabilities(
                format_name="JPEG",
                max_resolution=(65535, 65535),
                supports_transparency=False,
                supports_animation=False,
                lossless_compression=False,
                platform_compatibility=["web", "mobile", "print", "social_media"]
            )
            
            self._format_capabilities["png"] = FormatCapabilities(
                format_name="PNG",
                max_resolution=(2147483647, 2147483647),
                supports_transparency=True,
                supports_animation=False,
                lossless_compression=True,
                platform_compatibility=["web", "mobile", "print"]
            )
            
            self._format_capabilities["webp"] = FormatCapabilities(
                format_name="WebP",
                max_resolution=(16383, 16383),
                supports_transparency=True,
                supports_animation=True,
                lossless_compression=True,
                platform_compatibility=["web", "mobile"]
            )
            
            # Video format capabilities
            self._format_capabilities["mp4"] = FormatCapabilities(
                format_name="MP4",
                supported_codecs=["H.264", "H.265", "AV1"],
                max_resolution=(7680, 4320),  # 8K
                supports_metadata=True,
                platform_compatibility=["web", "mobile", "social_media", "streaming"]
            )
            
            # Audio format capabilities
            self._format_capabilities["mp3"] = FormatCapabilities(
                format_name="MP3",
                max_duration=None,
                lossless_compression=False,
                platform_compatibility=["web", "mobile", "streaming"]
            )
            
        except Exception as e:
            self.logger.error(f"Format capabilities loading failed: {e}")
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a conversion job"""
        try:
            job = self._active_jobs.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error_message": "Job not found"
                }
            
            return {
                "success": True,
                "job_id": job_id,
                "status": job.status,
                "progress": job.progress,
                "input_format": job.input_format.value,
                "output_format": job.output_format.value,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "processing_time": job.processing_time,
                "output_path": job.output_path,
                "compression_ratio": job.compression_ratio,
                "error_message": job.error_message
            }
            
        except Exception as e:
            self.logger.error(f"Job status retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return {
            "success": True,
            "statistics": self._stats,
            "active_jobs": len(self._active_jobs)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the format processor"""
        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "image_conversion_available": IMAGE_CONVERSION_AVAILABLE,
            "video_conversion_available": VIDEO_CONVERSION_AVAILABLE,
            "audio_conversion_available": AUDIO_CONVERSION_AVAILABLE,
            "document_conversion_available": DOCUMENT_CONVERSION_AVAILABLE,
            "optimization_libs_available": OPTIMIZATION_LIBS_AVAILABLE,
            "active_jobs": len(self._active_jobs),
            "total_conversions": self._stats["total_conversions"],
            "success_rate": (
                self._stats["successful_conversions"] / self._stats["total_conversions"]
                if self._stats["total_conversions"] > 0 else 1.0
            ),
            "supported_formats": len(self._format_capabilities),
            "config": self.config.__dict__
        }
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the format processor"""
        try:
            # Cancel active jobs
            for job in self._active_jobs.values():
                if job.status == "processing":
                    job.status = "cancelled"
            
            # Cleanup temp directory
            if self.config.cleanup_temp_files and self.config.temp_directory:
                try:
                    shutil.rmtree(self.config.temp_directory)
                except:
                    pass
            
            self.logger.info("Format processor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


async def create_format_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> FormatProcessor:
    """
    Factory function to create and initialize a format processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized FormatProcessor instance
    """
    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = FormatProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in FormatProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = FormatProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
