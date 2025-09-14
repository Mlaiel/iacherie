"""
Video Processing Utilities - Professional Video Management System
================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive video processing utilities supporting:
- Professional video format conversion and processing
- Metadata extraction and manipulation
- Video quality analysis and optimization
- Performance optimized operations
- Multi-codec and container support

Expert Roles Covered:
- Audio Engineer: Video/audio synchronization and processing
- Backend Senior: Video file management and processing pipelines
- ML Engineer: Video analysis and content recognition
- DevOps Expert: Performance monitoring and batch processing
"""

import os
import subprocess
import tempfile
import hashlib
import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import math
import re

logger = logging.getLogger(__name__)


class VideoCodec(Enum):
    """Video codec types"""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"
    PRORES = "prores"
    DNX = "dnxhd"
    MJPEG = "mjpeg"
    MPEG2 = "mpeg2video"
    MPEG4 = "mpeg4"


class AudioCodec(Enum):
    """Audio codec types"""
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    FLAC = "flac"
    PCM = "pcm_s16le"
    AC3 = "ac3"
    DTS = "dts"


class VideoContainer(Enum):
    """Video container formats"""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"
    TS = "ts"


class VideoQuality(Enum):
    """Video quality presets"""
    ULTRA_LOW = "ultra_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"
    LOSSLESS = "lossless"


class VideoOperation(Enum):
    """Video operation types"""
    CONVERT = "convert"
    COMPRESS = "compress"
    EXTRACT_FRAMES = "extract_frames"
    EXTRACT_AUDIO = "extract_audio"
    ADD_WATERMARK = "add_watermark"
    RESIZE = "resize"
    TRIM = "trim"
    MERGE = "merge"
    ANALYZE = "analyze"


@dataclass
class VideoMetadata:
    """Video file metadata"""
    file_path: str
    file_size: int
    duration: float
    width: int
    height: int
    frame_rate: float
    bit_rate: int
    video_codec: str
    audio_codec: str
    container: str
    aspect_ratio: str
    color_space: str
    has_audio: bool
    audio_channels: int
    audio_sample_rate: int
    creation_time: Optional[datetime] = None
    metadata_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class VideoProcessingResult:
    """Result of video processing operation"""
    success: bool
    operation: VideoOperation
    input_file: str
    output_file: Optional[str] = None
    metadata: Optional[VideoMetadata] = None
    processing_time: float = 0.0
    file_size_before: int = 0
    file_size_after: int = 0
    compression_ratio: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class VideoConversionSettings:
    """Video conversion settings"""
    output_codec: VideoCodec = VideoCodec.H264
    audio_codec: AudioCodec = AudioCodec.AAC
    container: VideoContainer = VideoContainer.MP4
    quality: VideoQuality = VideoQuality.HIGH
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    audio_bit_rate: Optional[int] = None
    two_pass: bool = False
    hardware_acceleration: bool = True
    custom_options: Dict[str, str] = field(default_factory=dict)


class VideoUtilities:
    """
    Professional video processing utilities for content management platforms.
    
    Features:
    - High-quality video conversion and compression
    - Metadata extraction and manipulation
    - Video analysis and quality assessment
    - Batch processing capabilities
    - Hardware acceleration support
    - Performance monitoring and optimization
    """
    
    def __init__(self,
                 ffmpeg_path -> None: Optional[str] = None,
                 ffprobe_path -> None: Optional[str] = None,
                 temp_dir -> None: Optional[str] = None,
                 max_concurrent_jobs -> None: int = 4,
                 enable_hardware_acceleration -> None: bool = True,
                 quality_presets -> None: Optional[Dict[VideoQuality, Dict]] = None) -> None:
        """
        Initialize video utilities
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
            ffprobe_path: Path to FFprobe executable
            temp_dir: Temporary directory for processing
            max_concurrent_jobs: Maximum concurrent processing jobs
            enable_hardware_acceleration: Whether to use hardware acceleration
            quality_presets: Custom quality preset configurations
        """
        try:
            logger.info("Initializing VideoUtilities")
            
            # Tool paths
            self.ffmpeg_path = ffmpeg_path or self._find_executable("ffmpeg")
            self.ffprobe_path = ffprobe_path or self._find_executable("ffprobe")
            
            if not self.ffmpeg_path or not self.ffprobe_path:
                raise RuntimeError("FFmpeg and FFprobe must be installed and accessible")
            
            # Configuration
            self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "video_processing"
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            self.max_concurrent_jobs = max_concurrent_jobs
            self.enable_hardware_acceleration = enable_hardware_acceleration
            
            # Semaphore for controlling concurrent operations
            self.processing_semaphore = asyncio.Semaphore(max_concurrent_jobs)
            
            # Quality presets
            self.quality_presets = quality_presets or self._get_default_quality_presets()
            
            # Supported formats
            self.supported_input_formats = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', 
                                          '.wmv', '.m4v', '.3gp', '.ts', '.mts', '.m2ts'}
            
            # Hardware acceleration codecs
            self.hw_codecs = {
                'nvidia': {'h264': 'h264_nvenc', 'h265': 'hevc_nvenc'},
                'intel': {'h264': 'h264_qsv', 'h265': 'hevc_qsv'},
                'amd': {'h264': 'h264_amf', 'h265': 'hevc_amf'}
            }
            
            # Processing statistics
            self.processing_stats = {
                "total_jobs": 0,
                "successful_jobs": 0,
                "failed_jobs": 0,
                "total_processing_time": 0.0,
                "total_input_size": 0,
                "total_output_size": 0
            }
            
            logger.info("VideoUtilities initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize VideoUtilities: {e}")
            raise

    async def get_video_metadata(self, file_path: str) -> VideoMetadata:
        """
        Extract comprehensive video metadata
        
        Args:
            file_path: Path to video file
            
        Returns:
            VideoMetadata object with file information
        """
        try:
            logger.info(f"Extracting metadata from: {file_path}")
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Video file not found: {file_path}")
            
            # Use FFprobe to extract metadata
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {stderr.decode()}")
            
            # Parse JSON output
            probe_data = json.loads(stdout.decode())
            
            # Extract video stream info
            video_stream = None
            audio_stream = None
            
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream
            
            if not video_stream:
                raise ValueError("No video stream found in file")
            
            # Extract format info
            format_info = probe_data.get('format', {})
            
            # Calculate aspect ratio
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            aspect_ratio = f"{width}:{height}"
            if width and height:
                gcd = math.gcd(width, height)
                aspect_ratio = f"{width//gcd}:{height//gcd}"
            
            # Parse creation time
            creation_time = None
            creation_time_str = format_info.get('tags', {}).get('creation_time')
            if creation_time_str:
                try:
                    creation_time = datetime.fromisoformat(creation_time_str.replace('Z', '+00:00'))
                except:
                    pass
            
            # Create metadata object
            metadata = VideoMetadata(
                file_path=file_path,
                file_size=int(format_info.get('size', 0)),
                duration=float(format_info.get('duration', 0)),
                width=width,
                height=height,
                frame_rate=eval(video_stream.get('r_frame_rate', '0/1')),
                bit_rate=int(format_info.get('bit_rate', 0)),
                video_codec=video_stream.get('codec_name', 'unknown'),
                audio_codec=audio_stream.get('codec_name', 'none') if audio_stream else 'none',
                container=format_info.get('format_name', 'unknown'),
                aspect_ratio=aspect_ratio,
                color_space=video_stream.get('color_space', 'unknown'),
                has_audio=audio_stream is not None,
                audio_channels=int(audio_stream.get('channels', 0)) if audio_stream else 0,
                audio_sample_rate=int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
                creation_time=creation_time,
                metadata_tags=format_info.get('tags', {})
            )
            
            logger.info(f"Metadata extracted successfully: {file_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            raise

    async def convert_video(self,
                           input_file: str,
                           output_file: str,
                           settings: Optional[VideoConversionSettings] = None,
                           progress_callback: Optional[Callable] = None) -> VideoProcessingResult:
        """
        Convert video file with specified settings
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            settings: Conversion settings
            progress_callback: Optional progress callback function
            
        Returns:
            VideoProcessingResult with conversion details
        """
        async with self.processing_semaphore:
            start_time = datetime.now()
            
            try:
                logger.info(f"Converting video: {input_file} -> {output_file}")
                
                if not Path(input_file).exists():
                    raise FileNotFoundError(f"Input file not found: {input_file}")
                
                settings = settings or VideoConversionSettings()
                
                # Get input metadata
                input_metadata = await self.get_video_metadata(input_file)
                input_size = input_metadata.file_size
                
                # Create output directory
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Build FFmpeg command
                cmd = await self._build_ffmpeg_command(input_file, output_file, settings, input_metadata)
                
                # Execute conversion
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode()
                    raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")
                
                # Get output metadata
                output_metadata = await self.get_video_metadata(output_file)
                output_size = output_metadata.file_size
                
                # Calculate processing time and compression ratio
                processing_time = (datetime.now() - start_time).total_seconds()
                compression_ratio = input_size / output_size if output_size > 0 else 0
                
                # Update statistics
                self._update_processing_stats(True, processing_time, input_size, output_size)
                
                result = VideoProcessingResult(
                    success=True,
                    operation=VideoOperation.CONVERT,
                    input_file=input_file,
                    output_file=output_file,
                    metadata=output_metadata,
                    processing_time=processing_time,
                    file_size_before=input_size,
                    file_size_after=output_size,
                    compression_ratio=compression_ratio
                )
                
                logger.info(f"Video conversion completed: {input_file} -> {output_file}")
                return result
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                self._update_processing_stats(False, processing_time, 0, 0)
                
                logger.error(f"Video conversion failed: {input_file} -> {output_file}: {e}")
                
                return VideoProcessingResult(
                    success=False,
                    operation=VideoOperation.CONVERT,
                    input_file=input_file,
                    output_file=output_file,
                    processing_time=processing_time,
                    error_message=str(e)
                )

    async def compress_video(self,
                           input_file: str,
                           output_file: str,
                           target_size_mb: Optional[int] = None,
                           quality: VideoQuality = VideoQuality.HIGH) -> VideoProcessingResult:
        """
        Compress video to target size or quality
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            target_size_mb: Target file size in MB
            quality: Quality preset if no target size specified
            
        Returns:
            VideoProcessingResult with compression details
        """
        try:
            logger.info(f"Compressing video: {input_file}")
            
            # Get input metadata
            input_metadata = await self.get_video_metadata(input_file)
            
            settings = VideoConversionSettings()
            
            if target_size_mb:
                # Calculate target bitrate for desired file size
                target_size_bits = target_size_mb * 8 * 1024 * 1024
                target_bitrate = int(target_size_bits / input_metadata.duration)
                
                # Reserve 20% for audio
                video_bitrate = int(target_bitrate * 0.8)
                audio_bitrate = int(target_bitrate * 0.2)
                
                settings.bit_rate = video_bitrate
                settings.audio_bit_rate = min(audio_bitrate, 128000)  # Max 128k for audio
                settings.two_pass = True
            else:
                # Use quality preset
                preset = self.quality_presets[quality]
                settings.bit_rate = preset.get('video_bitrate')
                settings.audio_bit_rate = preset.get('audio_bitrate')
                settings.quality = quality
            
            # Perform conversion
            result = await self.convert_video(input_file, output_file, settings)
            result.operation = VideoOperation.COMPRESS
            
            return result
            
        except Exception as e:
            logger.error(f"Video compression failed: {input_file}: {e}")
            
            return VideoProcessingResult(
                success=False,
                operation=VideoOperation.COMPRESS,
                input_file=input_file,
                output_file=output_file,
                error_message=str(e)
            )

    async def extract_frames(self,
                           input_file: str,
                           output_dir: str,
                           frame_rate: float = 1.0,
                           start_time: Optional[float] = None,
                           duration: Optional[float] = None,
                           image_format: str = "jpg") -> VideoProcessingResult:
        """
        Extract frames from video
        
        Args:
            input_file: Path to input video file
            output_dir: Directory to save extracted frames
            frame_rate: Frames per second to extract
            start_time: Start time in seconds
            duration: Duration in seconds
            image_format: Output image format (jpg, png, etc.)
            
        Returns:
            VideoProcessingResult with extraction details
        """
        async with self.processing_semaphore:
            start_time_proc = datetime.now()
            
            try:
                logger.info(f"Extracting frames from: {input_file}")
                
                if not Path(input_file).exists():
                    raise FileNotFoundError(f"Input file not found: {input_file}")
                
                # Create output directory
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Build FFmpeg command
                output_pattern = output_path / f"frame_%06d.{image_format}"
                
                cmd = [
                    self.ffmpeg_path,
                    "-v", "quiet",
                    "-y"  # Overwrite output files
                ]
                
                # Add start time if specified
                if start_time is not None:
                    cmd.extend(["-ss", str(start_time)])
                
                cmd.extend(["-i", input_file])
                
                # Add duration if specified
                if duration is not None:
                    cmd.extend(["-t", str(duration)])
                
                # Frame extraction settings
                cmd.extend([
                    "-vf", f"fps={frame_rate}",
                    "-q:v", "2",  # High quality
                    str(output_pattern)
                ])
                
                # Execute command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode()
                    raise RuntimeError(f"Frame extraction failed: {error_msg}")
                
                # Count extracted frames
                frame_files = list(output_path.glob(f"frame_*.{image_format}"))
                
                processing_time = (datetime.now() - start_time_proc).total_seconds()
                
                result = VideoProcessingResult(
                    success=True,
                    operation=VideoOperation.EXTRACT_FRAMES,
                    input_file=input_file,
                    output_file=str(output_path),
                    processing_time=processing_time,
                    warnings=[f"Extracted {len(frame_files)} frames"]
                )
                
                logger.info(f"Frame extraction completed: {len(frame_files)} frames")
                return result
                
            except Exception as e:
                processing_time = (datetime.now() - start_time_proc).total_seconds()
                
                logger.error(f"Frame extraction failed: {input_file}: {e}")
                
                return VideoProcessingResult(
                    success=False,
                    operation=VideoOperation.EXTRACT_FRAMES,
                    input_file=input_file,
                    output_file=output_dir,
                    processing_time=processing_time,
                    error_message=str(e)
                )

    async def extract_audio(self,
                          input_file: str,
                          output_file: str,
                          audio_format: str = "mp3",
                          quality: str = "high") -> VideoProcessingResult:
        """
        Extract audio from video file
        
        Args:
            input_file: Path to input video file
            output_file: Path to output audio file
            audio_format: Output audio format
            quality: Audio quality (low, medium, high)
            
        Returns:
            VideoProcessingResult with extraction details
        """
        async with self.processing_semaphore:
            start_time = datetime.now()
            
            try:
                logger.info(f"Extracting audio from: {input_file}")
                
                if not Path(input_file).exists():
                    raise FileNotFoundError(f"Input file not found: {input_file}")
                
                # Create output directory
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Quality settings
                quality_settings = {
                    "low": {"bitrate": "64k"},
                    "medium": {"bitrate": "128k"},
                    "high": {"bitrate": "192k"}
                }
                
                bitrate = quality_settings.get(quality, quality_settings["high"])["bitrate"]
                
                # Build FFmpeg command
                cmd = [
                    self.ffmpeg_path,
                    "-v", "quiet",
                    "-y",  # Overwrite output files
                    "-i", input_file,
                    "-vn",  # No video
                    "-acodec", "mp3" if audio_format == "mp3" else "aac",
                    "-ab", bitrate,
                    output_file
                ]
                
                # Execute command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode()
                    raise RuntimeError(f"Audio extraction failed: {error_msg}")
                
                # Get output file size
                output_size = Path(output_file).stat().st_size
                processing_time = (datetime.now() - start_time).total_seconds()
                
                result = VideoProcessingResult(
                    success=True,
                    operation=VideoOperation.EXTRACT_AUDIO,
                    input_file=input_file,
                    output_file=output_file,
                    processing_time=processing_time,
                    file_size_after=output_size
                )
                
                logger.info(f"Audio extraction completed: {output_file}")
                return result
                
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                
                logger.error(f"Audio extraction failed: {input_file}: {e}")
                
                return VideoProcessingResult(
                    success=False,
                    operation=VideoOperation.EXTRACT_AUDIO,
                    input_file=input_file,
                    output_file=output_file,
                    processing_time=processing_time,
                    error_message=str(e)
                )

    async def resize_video(self,
                         input_file: str,
                         output_file: str,
                         width: int,
                         height: int,
                         maintain_aspect_ratio: bool = True) -> VideoProcessingResult:
        """
        Resize video to specified dimensions
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            width: Target width
            height: Target height
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            VideoProcessingResult with resize details
        """
        try:
            logger.info(f"Resizing video: {input_file} to {width}x{height}")
            
            settings = VideoConversionSettings()
            settings.width = width
            settings.height = height
            
            if maintain_aspect_ratio:
                # Add scaling filter to maintain aspect ratio
                settings.custom_options["vf"] = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            else:
                settings.custom_options["vf"] = f"scale={width}:{height}"
            
            result = await self.convert_video(input_file, output_file, settings)
            result.operation = VideoOperation.RESIZE
            
            return result
            
        except Exception as e:
            logger.error(f"Video resize failed: {input_file}: {e}")
            
            return VideoProcessingResult(
                success=False,
                operation=VideoOperation.RESIZE,
                input_file=input_file,
                output_file=output_file,
                error_message=str(e)
            )

    async def trim_video(self,
                        input_file: str,
                        output_file: str,
                        start_time: float,
                        duration: float) -> VideoProcessingResult:
        """
        Trim video to specified time range
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            VideoProcessingResult with trim details
        """
        async with self.processing_semaphore:
            start_time_proc = datetime.now()
            
            try:
                logger.info(f"Trimming video: {input_file} from {start_time}s for {duration}s")
                
                if not Path(input_file).exists():
                    raise FileNotFoundError(f"Input file not found: {input_file}")
                
                # Create output directory
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Build FFmpeg command
                cmd = [
                    self.ffmpeg_path,
                    "-v", "quiet",
                    "-y",  # Overwrite output files
                    "-ss", str(start_time),
                    "-i", input_file,
                    "-t", str(duration),
                    "-c", "copy",  # Stream copy for faster processing
                    output_file
                ]
                
                # Execute command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_msg = stderr.decode()
                    raise RuntimeError(f"Video trim failed: {error_msg}")
                
                # Get output metadata
                output_metadata = await self.get_video_metadata(output_file)
                processing_time = (datetime.now() - start_time_proc).total_seconds()
                
                result = VideoProcessingResult(
                    success=True,
                    operation=VideoOperation.TRIM,
                    input_file=input_file,
                    output_file=output_file,
                    metadata=output_metadata,
                    processing_time=processing_time,
                    file_size_after=output_metadata.file_size
                )
                
                logger.info(f"Video trim completed: {output_file}")
                return result
                
            except Exception as e:
                processing_time = (datetime.now() - start_time_proc).total_seconds()
                
                logger.error(f"Video trim failed: {input_file}: {e}")
                
                return VideoProcessingResult(
                    success=False,
                    operation=VideoOperation.TRIM,
                    input_file=input_file,
                    output_file=output_file,
                    processing_time=processing_time,
                    error_message=str(e)
                )

    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get video processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        total_jobs = self.processing_stats["total_jobs"]
        
        return {
            **self.processing_stats,
            "success_rate": (self.processing_stats["successful_jobs"] / max(total_jobs, 1)) * 100,
            "failure_rate": (self.processing_stats["failed_jobs"] / max(total_jobs, 1)) * 100,
            "average_processing_time": (self.processing_stats["total_processing_time"] / max(total_jobs, 1)),
            "total_compression_ratio": (self.processing_stats["total_input_size"] / 
                                      max(self.processing_stats["total_output_size"], 1))
        }

    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if video format is supported
        
        Args:
            file_path: Path to video file
            
        Returns:
            True if format is supported
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_input_formats

    # Private helper methods
    def _find_executable(self, name: str) -> Optional[str]:
        """Find executable in system PATH"""
        import shutil
        return shutil.which(name)

    async def _build_ffmpeg_command(self,
                                  input_file: str,
                                  output_file: str,
                                  settings: VideoConversionSettings,
                                  input_metadata: VideoMetadata) -> List[str]:
        """Build FFmpeg command based on settings"""
        cmd = [self.ffmpeg_path, "-v", "quiet", "-y"]
        
        # Hardware acceleration
        if settings.hardware_acceleration and self.enable_hardware_acceleration:
            # Try to detect and use hardware acceleration
            hw_codec = self._get_hardware_codec(settings.output_codec)
            if hw_codec:
                cmd.extend(["-hwaccel", "auto"])
        
        # Input file
        cmd.extend(["-i", input_file])
        
        # Video codec
        codec_name = settings.output_codec.value
        if settings.hardware_acceleration:
            hw_codec = self._get_hardware_codec(settings.output_codec)
            if hw_codec:
                codec_name = hw_codec
        
        cmd.extend(["-c:v", codec_name])
        
        # Audio codec
        cmd.extend(["-c:a", settings.audio_codec.value])
        
        # Quality/bitrate settings
        if settings.quality in self.quality_presets:
            preset = self.quality_presets[settings.quality]
            if "crf" in preset:
                cmd.extend(["-crf", str(preset["crf"])])
            elif settings.bit_rate:
                cmd.extend(["-b:v", str(settings.bit_rate)])
        
        # Audio bitrate
        if settings.audio_bit_rate:
            cmd.extend(["-b:a", str(settings.audio_bit_rate)])
        
        # Dimensions
        if settings.width and settings.height:
            cmd.extend(["-s", f"{settings.width}x{settings.height}"])
        
        # Frame rate
        if settings.frame_rate:
            cmd.extend(["-r", str(settings.frame_rate)])
        
        # Two-pass encoding
        if settings.two_pass:
            # This would require running two separate commands
            # Simplified for this implementation
            cmd.extend(["-preset", "slow"])
        
        # Custom options
        for key, value in settings.custom_options.items():
            cmd.extend([f"-{key}", value])
        
        # Output file
        cmd.append(output_file)
        
        return cmd

    def _get_hardware_codec(self, codec: VideoCodec) -> Optional[str]:
        """Get hardware accelerated codec if available"""
        # Simplified hardware codec detection
        # In a real implementation, you'd detect available hardware
        if codec == VideoCodec.H264:
            return "h264_nvenc"  # NVIDIA
        elif codec == VideoCodec.H265:
            return "hevc_nvenc"  # NVIDIA
        return None

    def _get_default_quality_presets(self) -> Dict[VideoQuality, Dict]:
        """Get default quality presets"""
        return {
            VideoQuality.ULTRA_LOW: {
                "video_bitrate": 200000,
                "audio_bitrate": 64000,
                "crf": 35
            },
            VideoQuality.LOW: {
                "video_bitrate": 500000,
                "audio_bitrate": 96000,
                "crf": 28
            },
            VideoQuality.MEDIUM: {
                "video_bitrate": 1000000,
                "audio_bitrate": 128000,
                "crf": 23
            },
            VideoQuality.HIGH: {
                "video_bitrate": 2000000,
                "audio_bitrate": 192000,
                "crf": 20
            },
            VideoQuality.ULTRA_HIGH: {
                "video_bitrate": 5000000,
                "audio_bitrate": 256000,
                "crf": 18
            },
            VideoQuality.LOSSLESS: {
                "video_bitrate": None,
                "audio_bitrate": None,
                "crf": 0
            }
        }

    def _update_processing_stats(self, success -> None: bool, processing_time -> None: float, 
                               input_size -> None: int, output_size -> None: int) -> None:
        """Update processing statistics"""
        self.processing_stats["total_jobs"] += 1
        self.processing_stats["total_processing_time"] += processing_time
        self.processing_stats["total_input_size"] += input_size
        self.processing_stats["total_output_size"] += output_size
        
        if success:
            self.processing_stats["successful_jobs"] += 1
        else:
            self.processing_stats["failed_jobs"] += 1


# Utility functions
async def quick_video_info(file_path: str) -> Dict[str, Any]:
    """
    Quick video file information
    
    Args:
        file_path: Path to video file
        
    Returns:
        Dictionary with basic video information
    """
    utils = VideoUtilities()
    try:
        metadata = await utils.get_video_metadata(file_path)
        return {
            "duration": metadata.duration,
            "resolution": f"{metadata.width}x{metadata.height}",
            "size_mb": round(metadata.file_size / (1024 * 1024), 2),
            "codec": metadata.video_codec,
            "container": metadata.container
        }
    except Exception as e:
        return {"error": str(e)}


def get_video_thumbnail_time(duration: float) -> float:
    """
    Get optimal time for video thumbnail extraction
    
    Args:
        duration: Video duration in seconds
        
    Returns:
        Optimal thumbnail time in seconds
    """
    # Usually 10% into the video, but not less than 1 second
    thumbnail_time = max(1.0, duration * 0.1)
    # But not more than 30 seconds
    return min(thumbnail_time, 30.0)


def calculate_video_bitrate(file_size_mb: float, duration_seconds: float) -> int:
    """
    Calculate video bitrate from file size and duration
    
    Args:
        file_size_mb: File size in megabytes
        duration_seconds: Duration in seconds
        
    Returns:
        Bitrate in bits per second
    """
    file_size_bits = file_size_mb * 8 * 1024 * 1024
    return int(file_size_bits / duration_seconds)


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1:23:45")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"