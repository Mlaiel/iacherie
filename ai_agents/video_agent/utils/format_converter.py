"""Video Format Converter - Advanced Multi-Format Video Conversion System

Industrial-grade video format conversion engine with optimized encoding,
compression algorithms, and professional-quality output for all major formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Video Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json
import subprocess
import hashlib

import cv2
import numpy as np
import ffmpeg
from PIL import Image

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.file_handler import SecureFileHandler
from ...models.video_models import ConversionJob, FormatProfile

logger = logging.getLogger(__name__)

class SupportedFormat:
    """
Comprehensive list of supported video formats"""
    # Standard formats
    MP4 = "mp4"
    AVI = "avi" 
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    MKV = "mkv"
    WEBM = "webm"
    M4V = "m4v"
    
    # Professional formats
    PRORES = "prores"
    DNX = "dnxhd"
    CINEFORM = "cfhd"
    
    # Streaming formats
    HLS = "hls"
    DASH = "dash"
    
    # Raw formats
    YUV = "yuv"
    RGB = "rgb"

class VideoCodecProfile:
    """Video codec profiles with optimized settings"""

    
    H264_BASELINE = {
        "codec": "libx264",
        "profile": "baseline",
        "level": "3.0",
        "compatibility": "universal",
        "description": "Maximum compatibility, lower quality"
    }
    
    H264_MAIN = {
        "codec": "libx264", 
        "profile": "main",
        "level": "4.0",
        "compatibility": "high",
        "description": "Good balance of quality and compatibility"
    }
    
    H264_HIGH = {
        "codec": "libx264",
        "profile": "high", 
        "level": "4.2",
        "compatibility": "medium",
        "description": "High quality, modern devices"
    }
    
    H265_MAIN = {
        "codec": "libx265",
        "profile": "main",
        "level": "4.1", 
        "compatibility": "limited",
        "description": "Excellent compression, newer devices"
    }
    
    VP9 = {
        "codec": "libvpx-vp9",
        "profile": "0",
        "level": "4.1",
        "compatibility": "web",
        "description": "Web optimized, open standard"
    }
    
    AV1 = {
        "codec": "libaom-av1",
        "profile": "main",
        "level": "4.1",
        "compatibility": "cutting_edge", 
        "description": "Future-proof, best compression"
    }

class AudioCodecProfile:
    """Audio codec profiles for different use cases"""

    
    AAC_LC = {
        "codec": "aac",
        "profile": "aac_low",
        "bitrate": "128k",
        "channels": 2,
        "sample_rate": 48000,
        "description": "Standard AAC for most uses"
    }
    
    AAC_HE = {
        "codec": "aac", 
        "profile": "aac_he",
        "bitrate": "64k",
        "channels": 2,
        "sample_rate": 48000,
        "description": "Efficient AAC for streaming"
    }
    
    MP3 = {
        "codec": "mp3",
        "bitrate": "128k", 
        "channels": 2,
        "sample_rate": 44100,
        "description": "Universal compatibility"
    }
    
    OPUS = {
        "codec": "libopus",
        "bitrate": "128k",
        "channels": 2,
        "sample_rate": 48000,
        "description": "High quality, low latency"
    }
    
    FLAC = {
        "codec": "flac",
        "channels": 2,
        "sample_rate": 48000,
        "description": "Lossless audio compression"
    }

class ConversionPreset:
    """Pre-configured conversion presets for common use cases"""

    
    SOCIAL_MEDIA = {
        "name": "Social Media",
        "video_codec": VideoCodecProfile.H264_MAIN,
        "audio_codec": AudioCodecProfile.AAC_LC,
        "resolution": "1080p",
        "fps": 30,
        "bitrate": "2500k",
        "optimization": "fast_decode"
    }
    
    STREAMING_HD = {
        "name": "HD Streaming", 
        "video_codec": VideoCodecProfile.H264_HIGH,
        "audio_codec": AudioCodecProfile.AAC_HE,
        "resolution": "720p",
        "fps": 30,
        "bitrate": "1500k",
        "optimization": "streaming"
    }
    
    STREAMING_4K = {
        "name": "4K Streaming",
        "video_codec": VideoCodecProfile.H265_MAIN,
        "audio_codec": AudioCodecProfile.AAC_LC,
        "resolution": "2160p",
        "fps": 30,
        "bitrate": "15000k",
        "optimization": "quality"
    }
    
    ARCHIVE = {
        "name": "Archive Quality",
        "video_codec": VideoCodecProfile.H264_HIGH,
        "audio_codec": AudioCodecProfile.FLAC,
        "resolution": "original",
        "fps": "original",
        "bitrate": "high",
        "optimization": "quality"
    }
    
    MOBILE = {
        "name": "Mobile Optimized",
        "video_codec": VideoCodecProfile.H264_BASELINE,
        "audio_codec": AudioCodecProfile.AAC_HE,
        "resolution": "480p",
        "fps": 24,
        "bitrate": "800k",
        "optimization": "size"
    }
    
    WEB_OPTIMIZED = {
        "name": "Web Optimized",
        "video_codec": VideoCodecProfile.VP9,
        "audio_codec": AudioCodecProfile.OPUS,
        "resolution": "1080p", 
        "fps": 30,
        "bitrate": "2000k",
        "optimization": "web"
    }

class VideoFormatConverter:
    """
    Advanced video format conversion system with optimized encoding algorithms.
    
    Provides comprehensive format conversion capabilities with professional-quality
    output, intelligent codec selection, and platform-specific optimizations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VideoFormatConverter with advanced configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "video_converter" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Conversion parameters
        self.max_file_size = self.config.get("max_file_size", 20 * 1024 * 1024 * 1024)  # 20GB
        self.max_duration = self.config.get("max_duration", 14400)  # 4 hours
        self.concurrent_jobs = self.config.get("concurrent_jobs", 2)
        
        # Hardware acceleration settings
        self.gpu_acceleration = self.config.get("gpu_acceleration", True)
        self.hardware_encoders = self._detect_hardware_encoders()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor("video_converter")
        self.file_handler = SecureFileHandler()
        
        # Quality profiles
        self.quality_profiles = {
            "draft": {"crf": 32, "preset": "ultrafast"},
            "fast": {"crf": 28, "preset": "fast"},
            "balanced": {"crf": 23, "preset": "medium"},
            "quality": {"crf": 18, "preset": "slow"},
            "archival": {"crf": 15, "preset": "veryslow"}
        }
        
        logger.info("VideoFormatConverter initialized with hardware acceleration support")
    
    def _detect_hardware_encoders(self) -> Dict[str, bool]:
        """Detect available hardware encoders"""
        encoders = {
            "nvenc": False,    # NVIDIA
            "qsv": False,      # Intel QuickSync
            "vaapi": False,    # Intel/AMD VAAPI
            "videotoolbox": False,  # Apple
            "amf": False       # AMD
        }
        
        try:
            # Check for NVIDIA NVENC
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True, timeout=10
            )
            
            output = result.stdout.lower()
            encoders["nvenc"] = "h264_nvenc" in output
            encoders["qsv"] = "h264_qsv" in output
            encoders["vaapi"] = "h264_vaapi" in output
            encoders["videotoolbox"] = "h264_videotoolbox" in output
            encoders["amf"] = "h264_amf" in output
            
        except Exception as e:
            logger.warning(f"Could not detect hardware encoders: {e}")
        
        return encoders
    
    async def convert_video(self, input_path: str,
                          output_format: str,
                          output_path: Optional[str] = None,
                          preset: Optional[str] = None,
                          custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert video to specified format with optimized settings.
        
        Args:
            input_path: Path to input video file
            output_format: Target format (mp4, mkv, webm, etc.)
            output_path: Optional output path
            preset: Conversion preset to use
            custom_settings: Custom conversion parameters
            
        Returns:
            Conversion result with detailed metadata
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        # Validate file size
        file_size = os.path.getsize(input_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File size {file_size} exceeds maximum {self.max_file_size}")
        
        if not output_path:
            input_name = Path(input_path).stem
            output_path = str(self.temp_dir / f"{input_name}_converted.{output_format}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Analyze input video
            input_info = await self._analyze_input_video(input_path)
            
            # Validate duration
            duration = input_info.get("duration", 0)
            if duration > self.max_duration:
                raise ValueError(f"Video duration {duration}s exceeds maximum {self.max_duration}s")
            
            # Select optimal conversion settings
            conversion_settings = await self._optimize_conversion_settings(
                input_info, output_format, preset, custom_settings
            )
            
            # Perform conversion
            conversion_result = await self._execute_conversion(
                input_path, output_path, conversion_settings
            )
            
            # Analyze output
            output_info = await self._analyze_input_video(output_path)
            
            # Calculate metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            size_reduction = 1 - (os.path.getsize(output_path) / file_size)
            
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "input_format": input_info.get("format_name"),
                "output_format": output_format,
                "preset": preset,
                "processing_time": processing_time,
                "input_info": input_info,
                "output_info": output_info,
                "conversion_settings": conversion_settings,
                "size_reduction_percent": size_reduction * 100,
                "file_size_mb": os.path.getsize(output_path) / (1024 * 1024),
                "hardware_acceleration_used": conversion_result.get("hardware_acceleration", False),
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            raise
    
    async def batch_convert(self, conversion_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert multiple videos in batch with optimal resource utilization.
        
        Args:
            conversion_jobs: List of conversion job configurations
            
        Returns:
            List of conversion results
        """
        if not conversion_jobs:
            return []
        
        # Limit concurrent jobs
        semaphore = asyncio.Semaphore(self.concurrent_jobs)
        
        async def convert_single_job(job):
            async with semaphore:
                try:
                    return await self.convert_video(
                        input_path=job["input_path"],
                        output_format=job["output_format"],
                        output_path=job.get("output_path"),
                        preset=job.get("preset"),
                        custom_settings=job.get("custom_settings")
                    )
                except Exception as e:
                    return {
                        "success": False,
                        "input_path": job["input_path"],
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        
        # Execute all conversion jobs
        results = await asyncio.gather(
            *[convert_single_job(job) for job in conversion_jobs],
            return_exceptions=True
        )
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "input_path": conversion_jobs[i]["input_path"],
                    "error": str(result),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def create_adaptive_stream(self, input_path: str,
                                   output_dir: str,
                                   resolutions: List[str] = None,
                                   format_type: str = "hls") -> Dict[str, Any]:
        """
        Create adaptive streaming formats (HLS/DASH) with multiple resolutions.
        
        Args:
            input_path: Path to input video
            output_dir: Directory for output files
            resolutions: List of target resolutions
            format_type: Streaming format type (hls or dash)
            
        Returns:
            Adaptive streaming creation result
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        resolutions = resolutions or ["240p", "360p", "480p", "720p", "1080p"]
        
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Analyze input
            input_info = await self._analyze_input_video(input_path)
            input_height = input_info.get("height", 1080)
            
            # Filter resolutions based on input
            valid_resolutions = self._filter_valid_resolutions(resolutions, input_height)
            
            # Create multiple quality streams
            stream_paths = []
            
            for resolution in valid_resolutions:
                resolution_settings = self._get_resolution_settings(resolution)
                stream_output = output_path / f"stream_{resolution}.m3u8"
                
                # Convert to streaming format
                success = await self._create_stream_variant(
                    input_path, str(stream_output), resolution_settings, format_type
                )
                
                if success:
                    stream_paths.append({
                        "resolution": resolution,
                        "path": str(stream_output),
                        "bitrate": resolution_settings["bitrate"]
                    })
            
            # Create master playlist
            if format_type == "hls":
                master_playlist = await self._create_hls_master_playlist(stream_paths, output_path)
            else:
                master_playlist = await self._create_dash_manifest(stream_paths, output_path)
            
            return {
                "success": True,
                "input_path": input_path,
                "output_directory": output_dir,
                "format_type": format_type,
                "resolutions": valid_resolutions,
                "stream_variants": len(stream_paths),
                "master_playlist": master_playlist,
                "total_files": len(list(output_path.glob("*"))),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Adaptive streaming creation failed: {e}")
            raise
    
    async def _analyze_input_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze input video properties using ffprobe"""
        try:
            probe = ffmpeg.probe(video_path)
            
            # Extract format information
            format_info = probe.get("format", {})
            
            # Find video stream
            video_stream = None
            audio_streams = []
            
            for stream in probe.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    audio_streams.append(stream)
            
            info = {
                "format_name": format_info.get("format_name"),
                "format_long_name": format_info.get("format_long_name"),
                "duration": float(format_info.get("duration", 0)),
                "size": int(format_info.get("size", 0)),
                "bitrate": int(format_info.get("bit_rate", 0)),
                "streams_total": len(probe.get("streams", []))
            }
            
            if video_stream:
                info.update({
                    "width": int(video_stream.get("width", 0)),
                    "height": int(video_stream.get("height", 0)),
                    "fps": self._parse_fps(video_stream.get("avg_frame_rate", "0/1")),
                    "video_codec": video_stream.get("codec_name"),
                    "video_profile": video_stream.get("profile"),
                    "video_level": video_stream.get("level"),
                    "pixel_format": video_stream.get("pix_fmt"),
                    "video_bitrate": int(video_stream.get("bit_rate", 0)),
                    "color_space": video_stream.get("color_space"),
                    "color_range": video_stream.get("color_range")
                })
            
            if audio_streams:
                primary_audio = audio_streams[0]
                info.update({
                    "audio_streams": len(audio_streams),
                    "audio_codec": primary_audio.get("codec_name"),
                    "audio_sample_rate": int(primary_audio.get("sample_rate", 0)),
                    "audio_channels": int(primary_audio.get("channels", 0)),
                    "audio_bitrate": int(primary_audio.get("bit_rate", 0)),
                    "audio_channel_layout": primary_audio.get("channel_layout")
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            raise
    
    def _parse_fps(self, fps_string: str) -> float:
        """Parse FPS from fraction string"""
        try:
            if "/" in fps_string:
                numerator, denominator = fps_string.split("/")
                return float(numerator) / float(denominator) if float(denominator) != 0 else 0
            else:
                return float(fps_string)
        except:
            return 0.0
    
    async def _optimize_conversion_settings(self, input_info: Dict[str, Any],
                                          output_format: str,
                                          preset: Optional[str],
                                          custom_settings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize conversion settings based on input and target requirements"""
        
        # Start with preset if provided
        if preset:
            settings = self._get_preset_settings(preset).copy()
        else:
            settings = self._get_default_settings(output_format).copy()
        
        # Apply custom settings
        if custom_settings:
            settings.update(custom_settings)
        
        # Optimize based on input characteristics
        input_width = input_info.get("width", 1920)
        input_height = input_info.get("height", 1080)
        input_fps = input_info.get("fps", 30)
        input_duration = input_info.get("duration", 0)
        
        # Adjust resolution if not specified
        if "resolution" not in settings or settings["resolution"] == "original":
            settings["width"] = input_width
            settings["height"] = input_height
        else:
            resolution_settings = self._get_resolution_settings(settings["resolution"])
            settings.update(resolution_settings)
        
        # Adjust frame rate
        if "fps" not in settings or settings["fps"] == "original":
            settings["fps"] = input_fps
        
        # Select optimal codec based on format and hardware
        settings["video_codec"] = self._select_optimal_video_codec(
            output_format, input_info, settings
        )
        settings["audio_codec"] = self._select_optimal_audio_codec(
            output_format, input_info, settings
        )
        
        # Hardware acceleration
        if self.gpu_acceleration:
            hw_codec = self._get_hardware_codec(settings["video_codec"])
            if hw_codec:
                settings["video_codec"] = hw_codec
                settings["hardware_acceleration"] = True
        
        # Optimize for file size vs quality
        if input_duration > 3600:  # Long videos (>1 hour)
            settings["crf"] = min(settings.get("crf", 23) + 2, 28)  # Lower quality for size
        elif input_duration < 300:  # Short videos (<5 minutes)  
            settings["crf"] = max(settings.get("crf", 23) - 2, 15)  # Higher quality
        
        return settings
    
    def _get_preset_settings(self, preset: str) -> Dict[str, Any]:
        """Get settings for predefined presets"""
        presets = {
            "social_media": ConversionPreset.SOCIAL_MEDIA,
            "streaming_hd": ConversionPreset.STREAMING_HD,
            "streaming_4k": ConversionPreset.STREAMING_4K,
            "archive": ConversionPreset.ARCHIVE,
            "mobile": ConversionPreset.MOBILE,
            "web_optimized": ConversionPreset.WEB_OPTIMIZED
        }
        
        return presets.get(preset, ConversionPreset.SOCIAL_MEDIA)
    
    def _get_default_settings(self, output_format: str) -> Dict[str, Any]:
        """Get default settings for specific output formats"""
        format_defaults = {
            "mp4": {
                "video_codec": "libx264",
                "audio_codec": "aac",
                "crf": 23,
                "preset": "medium"
            },
            "mkv": {
                "video_codec": "libx264", 
                "audio_codec": "aac",
                "crf": 20,
                "preset": "slow"
            },
            "webm": {
                "video_codec": "libvpx-vp9",
                "audio_codec": "libopus",
                "crf": 30,
                "preset": "medium"
            },
            "avi": {
                "video_codec": "libx264",
                "audio_codec": "mp3",
                "crf": 23,
                "preset": "medium"
            }
        }
        
        return format_defaults.get(output_format, format_defaults["mp4"])
    
    def _get_resolution_settings(self, resolution: str) -> Dict[str, Any]:
        """Get width, height, and bitrate for resolution preset"""
        resolutions = {
            "240p": {"width": 426, "height": 240, "bitrate": "400k"},
            "360p": {"width": 640, "height": 360, "bitrate": "800k"},
            "480p": {"width": 854, "height": 480, "bitrate": "1200k"},
            "720p": {"width": 1280, "height": 720, "bitrate": "2500k"},
            "1080p": {"width": 1920, "height": 1080, "bitrate": "5000k"},
            "1440p": {"width": 2560, "height": 1440, "bitrate": "10000k"},
            "2160p": {"width": 3840, "height": 2160, "bitrate": "20000k"}
        }
        
        return resolutions.get(resolution, resolutions["1080p"])
    
    def _select_optimal_video_codec(self, output_format: str, input_info: Dict[str, Any], 
                                   settings: Dict[str, Any]) -> str:
        """Select optimal video codec based on format and requirements"""
        
        # Format-specific codec preferences
        codec_preferences = {
            "mp4": ["libx264", "libx265"],
            "mkv": ["libx264", "libx265", "libvpx-vp9"],
            "webm": ["libvpx-vp9", "libvpx"],
            "avi": ["libx264", "libxvid"],
            "mov": ["libx264", "prores"]
        }
        
        preferred_codecs = codec_preferences.get(output_format, ["libx264"])
        
        # Consider input codec for potential stream copy
        input_codec = input_info.get("video_codec")
        if input_codec in preferred_codecs and settings.get("preserve_quality", False):
            return input_codec
        
        # Return first available codec
        return preferred_codecs[0]
    
    def _select_optimal_audio_codec(self, output_format: str, input_info: Dict[str, Any],
                                   settings: Dict[str, Any]) -> str:
        """Select optimal audio codec based on format"""
        
        codec_preferences = {
            "mp4": ["aac", "mp3"],
            "mkv": ["aac", "flac", "mp3"],
            "webm": ["libopus", "libvorbis"],
            "avi": ["mp3", "aac"],
            "mov": ["aac", "alac"]
        }
        
        preferred_codecs = codec_preferences.get(output_format, ["aac"])
        return preferred_codecs[0]
    
    def _get_hardware_codec(self, software_codec: str) -> Optional[str]:
        """Get hardware-accelerated equivalent of software codec"""
        
        hw_codec_map = {
            "libx264": {
                "nvenc": "h264_nvenc",
                "qsv": "h264_qsv", 
                "vaapi": "h264_vaapi",
                "videotoolbox": "h264_videotoolbox",
                "amf": "h264_amf"
            },
            "libx265": {
                "nvenc": "hevc_nvenc",
                "qsv": "hevc_qsv",
                "vaapi": "hevc_vaapi",
                "videotoolbox": "hevc_videotoolbox",
                "amf": "hevc_amf"
            }
        }
        
        codec_variants = hw_codec_map.get(software_codec, {})
        
        # Return first available hardware encoder
        for hw_type, hw_codec in codec_variants.items():
            if self.hardware_encoders.get(hw_type, False):
                logger.info(f"Using hardware encoder: {hw_codec}")
                return hw_codec
        
        return None
    
    async def _execute_conversion(self, input_path: str, output_path: str, 
                                settings: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual video conversion"""
        
        try:
            # Build ffmpeg command
            input_stream = ffmpeg.input(input_path)
            
            # Video encoding options
            video_options = {
                "vcodec": settings["video_codec"],
                "crf": settings.get("crf", 23),
                "preset": settings.get("preset", "medium")
            }
            
            # Add resolution scaling if needed
            if "width" in settings and "height" in settings:
                video_options["vf"] = f"scale={settings['width']}:{settings['height']}"
            
            # Add frame rate if specified
            if "fps" in settings:
                video_options["r"] = settings["fps"]
            
            # Audio encoding options
            audio_options = {
                "acodec": settings["audio_codec"]
            }
            
            if "audio_bitrate" in settings:
                audio_options["audio_bitrate"] = settings["audio_bitrate"]
            
            # Combine all options
            output_options = {**video_options, **audio_options}
            
            # Add format-specific options
            if output_path.endswith('.mp4'):
                output_options["movflags"] = "+faststart"  # Web optimization
            
            # Create output stream
            output_stream = ffmpeg.output(input_stream, output_path, **output_options)
            
            # Execute conversion
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "success": True,
                "hardware_acceleration": settings.get("hardware_acceleration", False),
                "final_codec": settings["video_codec"],
                "encoding_options": output_options
            }
            
        except Exception as e:
            logger.error(f"Conversion execution failed: {e}")
            raise
    
    def _filter_valid_resolutions(self, resolutions: List[str], input_height: int) -> List[str]:
        """Filter resolutions that are smaller or equal to input resolution"""
        
        resolution_heights = {
            "240p": 240, "360p": 360, "480p": 480,
            "720p": 720, "1080p": 1080, "1440p": 1440, "2160p": 2160
        }
        
        return [res for res in resolutions if resolution_heights.get(res, 0) <= input_height]
    
    async def _create_stream_variant(self, input_path: str, output_path: str,
                                   resolution_settings: Dict[str, Any], format_type: str) -> bool:
        """Create a single streaming variant"""
        
        try:
            input_stream = ffmpeg.input(input_path)
            
            # HLS-specific settings
            if format_type == "hls":
                output_options = {
                    "vcodec": "libx264",
                    "acodec": "aac",
                    "vf": f"scale={resolution_settings['width']}:{resolution_settings['height']}",
                    "b:v": resolution_settings["bitrate"],
                    "b:a": "128k",
                    "hls_time": 10,
                    "hls_playlist_type": "vod",
                    "f": "hls"
                }
            else:  # DASH
                output_options = {
                    "vcodec": "libx264",
                    "acodec": "aac", 
                    "vf": f"scale={resolution_settings['width']}:{resolution_settings['height']}",
                    "b:v": resolution_settings["bitrate"],
                    "b:a": "128k",
                    "f": "dash"
                }
            
            output_stream = ffmpeg.output(input_stream, output_path, **output_options)
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Stream variant creation failed: {e}")
            return False
    
    async def _create_hls_master_playlist(self, stream_paths: List[Dict[str, Any]], 
                                        output_dir: Path) -> str:
        """Create HLS master playlist"""
        
        master_playlist_path = output_dir / "master.m3u8"
        
        try:
            with open(master_playlist_path, 'w') as f:
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n\n")
                
                for stream in stream_paths:
                    resolution = stream["resolution"]
                    bitrate = stream["bitrate"].replace("k", "000")
                    filename = Path(stream["path"]).name
                    
                    resolution_settings = self._get_resolution_settings(resolution)
                    width = resolution_settings["width"]
                    height = resolution_settings["height"]
                    
                    f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={width}x{height}\n")
                    f.write(f"{filename}\n")
            
            return str(master_playlist_path)
            
        except Exception as e:
            logger.error(f"HLS master playlist creation failed: {e}")
            return ""
    
    async def _create_dash_manifest(self, stream_paths: List[Dict[str, Any]], 
                                  output_dir: Path) -> str:
        """Create DASH manifest file"""
        
        manifest_path = output_dir / "manifest.mpd"
        
        # This would create a proper DASH MPD file
        # Implementation simplified for brevity
        try:
            with open(manifest_path, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">\n')
                f.write('  <!-- DASH manifest content would go here -->\n')
                f.write('</MPD>\n')
            
            return str(manifest_path)
            
        except Exception as e:
            logger.error(f"DASH manifest creation failed: {e}")
            return ""
    
    async def cleanup(self):
        """Cleanup temporary files and resources"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("VideoFormatConverter cleanup completed")
            
        except Exception as e:
            logger.error(f"VideoFormatConverter cleanup failed: {e}")


class CompressionOptimizer:
    """
    Advanced video compression optimizer with intelligent bitrate allocation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize CompressionOptimizer"""
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "compression_optimizer" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("CompressionOptimizer initialized")
    
    async def optimize_compression(self, input_path: str,
                                 target_size_mb: Optional[float] = None,
                                 target_quality: Optional[str] = None,
                                 output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize video compression for target size or quality.
        
        Args:
            input_path: Path to input video
            target_size_mb: Target file size in MB
            target_quality: Target quality level
            output_path: Optional output path
            
        Returns:
            Compression optimization result
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if not output_path:
            output_path = str(self.temp_dir / f"optimized_video_{uuid.uuid4()}.mp4")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Analyze input video
            video_info = await self._analyze_video_complexity(input_path)
            
            if target_size_mb:
                # Optimize for target file size
                result = await self._optimize_for_size(input_path, output_path, target_size_mb, video_info)
            elif target_quality:
                # Optimize for target quality
                result = await self._optimize_for_quality(input_path, output_path, target_quality, video_info)
            else:
                # Default optimization
                result = await self._optimize_default(input_path, output_path, video_info)
            
            optimization_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result.update({
                "input_path": input_path,
                "output_path": output_path,
                "optimization_time": optimization_time,
                "input_analysis": video_info,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Compression optimization failed: {e}")
            raise
    
    async def _analyze_video_complexity(self, video_path: str) -> Dict[str, Any]:
        """Analyze video complexity for compression optimization"""
        
        try:
            # Basic video properties
            probe = ffmpeg.probe(video_path)
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            duration = float(video_stream.get('duration', 0))
            bitrate = int(video_stream.get('bit_rate', 0))
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            # Analyze motion and complexity (simplified)
            complexity_score = await self._calculate_complexity_score(video_path)
            
            return {
                "duration": duration,
                "bitrate": bitrate,
                "width": width,
                "height": height,
                "pixel_count": width * height,
                "complexity_score": complexity_score,
                "recommended_bitrate": self._calculate_recommended_bitrate(width, height, complexity_score)
            }
            
        except Exception as e:
            logger.error(f"Video complexity analysis failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_complexity_score(self, video_path: str) -> float:
        """Calculate video complexity score based on motion and detail"""
        
        try:
            # Sample a few frames for analysis
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            complexity_scores = []
            
            # Sample 10 frames throughout the video
            for i in range(0, frame_count, max(1, frame_count // 10)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret:
                    # Calculate complexity based on edge density
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, 50, 150)
                    edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                    complexity_scores.append(edge_density)
            
            cap.release()
            
            return np.mean(complexity_scores) if complexity_scores else 0.5
            
        except Exception as e:
            logger.warning(f"Complexity calculation failed: {e}")
            return 0.5  # Default medium complexity
    
    def _calculate_recommended_bitrate(self, width: int, height: int, complexity: float) -> int:
        """Calculate recommended bitrate based on resolution and complexity"""
        
        # Base bitrate per pixel (bits per second per pixel)
        base_bpp = 0.05  # Conservative estimate
        
        # Adjust based on complexity
        complexity_multiplier = 0.5 + complexity * 1.5  # Range: 0.5 - 2.0
        
        # Calculate bitrate
        pixel_count = width * height
        recommended_bitrate = int(pixel_count * base_bpp * complexity_multiplier)
        
        # Clamp to reasonable ranges
        min_bitrate = 500000  # 500 kbps
        max_bitrate = 50000000  # 50 Mbps
        
        return max(min_bitrate, min(max_bitrate, recommended_bitrate))
    
    async def _optimize_for_size(self, input_path: str, output_path: str, 
                               target_size_mb: float, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize video for specific target file size"""
        
        try:
            duration = video_info.get("duration", 0)
            if duration == 0:
                raise ValueError("Could not determine video duration")
            
            # Calculate target bitrate (90% for video, 10% for audio)
            target_size_bits = target_size_mb * 8 * 1024 * 1024
            video_bitrate = int(target_size_bits * 0.9 / duration)
            audio_bitrate = "128k"
            
            # Ensure minimum quality
            min_bitrate = 200000  # 200 kbps minimum
            video_bitrate = max(video_bitrate, min_bitrate)
            
            # Two-pass encoding for better quality at target bitrate
            temp_log = str(self.temp_dir / "ffmpeg2pass")
            
            # First pass
            input_stream = ffmpeg.input(input_path)
            first_pass = ffmpeg.output(
                input_stream,
                "/dev/null",
                vcodec="libx264",
                b=str(video_bitrate),
                **{"pass": 1, "passlogfile": temp_log, "f": "null"}
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: first_pass.overwrite_output().run(quiet=True)
            )
            
            # Second pass
            second_pass = ffmpeg.output(
                input_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
                b=str(video_bitrate),
                **{"b:a": audio_bitrate, "pass": 2, "passlogfile": temp_log}
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: second_pass.overwrite_output().run(quiet=True)
            )
            
            # Check actual file size
            actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            size_accuracy = (target_size_mb - abs(target_size_mb - actual_size_mb)) / target_size_mb * 100
            
            return {
                "success": True,
                "optimization_type": "target_size",
                "target_size_mb": target_size_mb,
                "actual_size_mb": actual_size_mb,
                "size_accuracy_percent": size_accuracy,
                "target_bitrate": video_bitrate,
                "encoding_passes": 2
            }
            
        except Exception as e:
            logger.error(f"Size optimization failed: {e}")
            raise
    
    async def _optimize_for_quality(self, input_path: str, output_path: str,
                                  target_quality: str, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video for target quality level"""
        
        quality_settings = {
            "low": {"crf": 28, "preset": "fast"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"},
            "highest": {"crf": 15, "preset": "veryslow"}
        }
        
        settings = quality_settings.get(target_quality, quality_settings["medium"])
        
        try:
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
                crf=settings["crf"],
                preset=settings["preset"],
                **{"b:a": "128k"}
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            return {
                "success": True,
                "optimization_type": "target_quality",
                "target_quality": target_quality,
                "crf_used": settings["crf"],
                "preset_used": settings["preset"],
                "actual_size_mb": actual_size_mb,
                "encoding_passes": 1
            }
            
        except Exception as e:
            logger.error(f"Quality optimization failed: {e}")
            raise
    
    async def _optimize_default(self, input_path: str, output_path: str, 
                              video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default optimization balancing size and quality"""
        
        # Use recommended bitrate from analysis
        recommended_bitrate = video_info.get("recommended_bitrate", 2000000)
        
        try:
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
                crf=23,
                preset="medium",
                maxrate=str(recommended_bitrate),
                bufsize=str(recommended_bitrate * 2),
                **{"b:a": "128k"}
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            return {
                "success": True,
                "optimization_type": "balanced",
                "recommended_bitrate": recommended_bitrate,
                "crf_used": 23,
                "actual_size_mb": actual_size_mb,
                "encoding_passes": 1
            }
            
        except Exception as e:
            logger.error(f"Default optimization failed: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("CompressionOptimizer cleanup completed")
            
        except Exception as e:
            logger.error(f"CompressionOptimizer cleanup failed: {e}")
