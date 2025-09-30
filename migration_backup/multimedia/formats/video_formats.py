"""
🎬 VIDEO FORMATS PROCESSOR - ENTERPRISE ARCHITECTURE  
====================================================

Professional video format processing and optimization for Ainflue Platform
Supporting all modern video formats with AI-powered enhancement and conversion

**Expert Implementation:**
- Video Engineer: Professional video processing standards and codecs
- ML Engineer: AI-powered video analysis, quality assessment, and optimization
- Backend Senior: High-performance video processing pipelines
- Security Engineer: Video content validation and security compliance

**Supported Formats:** MP4, WebM, AV1, HEVC, H.264, MKV, MOV, AVI, FLV, WMV
**Features:** Advanced codec support, 4K/8K processing, HDR, Real-time transcoding
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes
import struct
import os
import json

# Video processing libraries
try:
    import cv2
    import ffmpeg
    import imageio
    import numpy as np
    from moviepy.editor import VideoFileClip
    import ffmpeg_streaming
except ImportError as e:
    logging.warning(f"Video processing dependencies not available: {e}")

from ..analytics.video_analytics import VideoQualityAnalyzer, VideoContentAnalyzer
from ..compression.video_compression import VideoCompressionEngine

logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    WEBM = "webm" 
    AV1 = "av1"
    HEVC = "hevc"
    H264 = "h264"
    MKV = "mkv"
    MOV = "mov"
    AVI = "avi"
    FLV = "flv"
    WMV = "wmv"
    MPEG = "mpeg"
    TS = "ts"

class VideoCodec(Enum):
    """Video codecs"""
    H264 = "h264"
    H265 = "h265"
    AV1 = "av1"
    VP8 = "vp8"
    VP9 = "vp9"
    MPEG4 = "mpeg4"
    MPEG2 = "mpeg2"
    PRORES = "prores"
    DNX = "dnx"

class VideoQuality(Enum):
    """Video quality presets"""
    LOW = "low"          # 480p, lower bitrate
    MEDIUM = "medium"    # 720p, medium bitrate
    HIGH = "high"        # 1080p, high bitrate
    ULTRA = "ultra"      # 4K, maximum bitrate
    HDR = "hdr"          # HDR content

@dataclass
class VideoFormatInfo:
    """Comprehensive video format information"""
    format_type: VideoFormat
    codec: VideoCodec
    resolution: Tuple[int, int]  # (width, height)
    fps: float
    duration: float
    bitrate: Optional[int]  # kbps
    file_size: int
    audio_codec: Optional[str]
    audio_channels: int
    quality_score: float
    metadata: Dict[str, Any]
    hdr_support: bool
    color_depth: int
    color_space: str

@dataclass
class VideoProcessingOptions:
    """Video processing configuration"""
    target_format: VideoFormat
    target_codec: VideoCodec
    target_resolution: Optional[Tuple[int, int]] = None
    target_fps: Optional[float] = None
    target_bitrate: Optional[int] = None
    quality_preset: VideoQuality = VideoQuality.HIGH
    enable_hdr: bool = False
    preserve_audio: bool = True
    optimize_for_streaming: bool = True
    hardware_acceleration: bool = True

class VideoCodecEngine:
    """Enterprise video codec engine with hardware acceleration"""
    
    def __init__(self):
        self.codec_profiles = {
            VideoCodec.H264: {
                'encoder': 'libx264',
                'profile': 'high',
                'level': '4.1',
                'preset': 'medium',
                'max_bitrate': 50000,  # kbps
                'hardware_encoders': ['h264_nvenc', 'h264_qsv', 'h264_videotoolbox']
            },
            VideoCodec.H265: {
                'encoder': 'libx265',
                'profile': 'main',
                'level': '5.1', 
                'preset': 'medium',
                'max_bitrate': 25000,  # 50% of H.264 for same quality
                'hardware_encoders': ['hevc_nvenc', 'hevc_qsv', 'hevc_videotoolbox']
            },
            VideoCodec.AV1: {
                'encoder': 'libaom-av1',
                'profile': 'main',
                'level': '5.1',
                'preset': 'medium',
                'max_bitrate': 15000,  # 30% of H.264 for same quality
                'hardware_encoders': ['av1_nvenc', 'av1_qsv']
            },
            VideoCodec.VP9: {
                'encoder': 'libvpx-vp9',
                'profile': 'profile-0',
                'preset': 'medium',
                'max_bitrate': 20000,
                'hardware_encoders': []
            },
            VideoCodec.VP8: {
                'encoder': 'libvpx',
                'preset': 'medium', 
                'max_bitrate': 30000,
                'hardware_encoders': []
            }
        }
        
        self.quality_presets = {
            VideoQuality.LOW: {
                'resolution': (854, 480),
                'bitrate_factor': 0.3,
                'fps': 24
            },
            VideoQuality.MEDIUM: {
                'resolution': (1280, 720),
                'bitrate_factor': 0.6,
                'fps': 30
            },
            VideoQuality.HIGH: {
                'resolution': (1920, 1080),
                'bitrate_factor': 1.0,
                'fps': 30
            },
            VideoQuality.ULTRA: {
                'resolution': (3840, 2160),
                'bitrate_factor': 3.0,
                'fps': 60
            }
        }
    
    def get_codec_profile(self, codec: VideoCodec) -> Dict[str, Any]:
        """Get codec profile configuration"""
        return self.codec_profiles.get(codec, {})
    
    def get_optimal_encoder(self, codec: VideoCodec, hardware_accel: bool = True) -> str:
        """Get optimal encoder for codec with hardware acceleration"""
        profile = self.get_codec_profile(codec)
        
        if hardware_accel:
            # Try hardware encoders first
            for hw_encoder in profile.get('hardware_encoders', []):
                if self._check_encoder_availability(hw_encoder):
                    return hw_encoder
        
        # Fallback to software encoder
        return profile.get('encoder', 'libx264')
    
    def _check_encoder_availability(self, encoder: str) -> bool:
        """Check if encoder is available in FFmpeg"""
        try:
            # Check with ffmpeg-python
            probe = ffmpeg.probe('test', f=encoder)
            return True
        except:
            return False
    
    def calculate_optimal_bitrate(self, resolution: Tuple[int, int], 
                                fps: float, quality: VideoQuality) -> int:
        """Calculate optimal bitrate based on resolution, fps, and quality"""
        width, height = resolution
        pixels = width * height
        
        # Base bitrate calculation (bits per pixel per frame)
        quality_preset = self.quality_presets.get(quality, self.quality_presets[VideoQuality.HIGH])
        bitrate_factor = quality_preset['bitrate_factor']
        
        # Baseline: 0.1 bits per pixel for medium quality 1080p@30fps
        base_bpp = 0.1 * bitrate_factor
        
        # Adjust for frame rate
        fps_factor = fps / 30.0
        
        # Calculate bitrate in kbps
        bitrate_kbps = int((pixels * base_bpp * fps_factor) / 1000)
        
        # Apply reasonable bounds
        min_bitrate = 500   # 500 kbps minimum
        max_bitrate = 50000 # 50 Mbps maximum
        
        return max(min_bitrate, min(bitrate_kbps, max_bitrate))

class VideoFormatProcessor:
    """Enterprise video format processor with AI capabilities"""
    
    def __init__(self):
        self.codec_engine = VideoCodecEngine()
        self.quality_analyzer = VideoQualityAnalyzer()
        self.content_analyzer = VideoContentAnalyzer()
        self.compression_engine = VideoCompressionEngine()
        self.supported_formats = list(VideoFormat)
        
    async def detect_format(self, file_path: Union[str, Path]) -> VideoFormatInfo:
        """Detect video format using multiple analysis methods"""
        file_path = Path(file_path)
        
        try:
            # Method 1: FFprobe analysis (most reliable)
            format_info = await self._analyze_with_ffprobe(file_path)
            if format_info:
                return format_info
            
            # Method 2: OpenCV analysis
            format_info = await self._analyze_with_opencv(file_path)
            if format_info:
                return format_info
            
            # Method 3: File extension + basic analysis
            return await self._basic_format_detection(file_path)
            
        except Exception as e:
            logger.error(f"Error detecting video format for {file_path}: {e}")
            raise
    
    async def _analyze_with_ffprobe(self, file_path: Path) -> Optional[VideoFormatInfo]:
        """Analyze video with FFprobe (most comprehensive)"""
        try:
            # Use ffmpeg-python to probe the file
            probe = ffmpeg.probe(str(file_path))
            
            # Extract video stream info
            video_stream = None
            audio_stream = None
            
            for stream in probe['streams']:
                if stream['codec_type'] == 'video' and video_stream is None:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            if not video_stream:
                return None
            
            # Extract format information
            format_container = probe['format']['format_name'].split(',')[0]
            format_type = self._map_container_to_format(format_container)
            
            # Extract codec information
            codec_name = video_stream.get('codec_name', '')
            codec = self._map_codec_name(codec_name)
            
            # Extract video properties
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            # Calculate FPS
            fps_str = video_stream.get('r_frame_rate', '0/1')
            fps = eval(fps_str) if '/' in fps_str else float(fps_str)
            
            # Duration
            duration = float(probe['format'].get('duration', 0))
            
            # Bitrate
            bitrate = int(probe['format'].get('bit_rate', 0)) // 1000  # Convert to kbps
            
            # File size
            file_size = int(probe['format'].get('size', 0))
            
            # Audio information
            audio_codec = audio_stream.get('codec_name') if audio_stream else None
            audio_channels = int(audio_stream.get('channels', 0)) if audio_stream else 0
            
            # Color information
            color_space = video_stream.get('color_space', 'unknown')
            color_depth = self._extract_color_depth(video_stream)
            
            # HDR detection
            hdr_support = self._detect_hdr_support(video_stream)
            
            # Quality analysis
            quality_score = await self._analyze_video_quality(file_path, video_stream)
            
            # Extract metadata
            metadata = probe['format'].get('tags', {})
            
            return VideoFormatInfo(
                format_type=format_type,
                codec=codec,
                resolution=(width, height),
                fps=fps,
                duration=duration,
                bitrate=bitrate,
                file_size=file_size,
                audio_codec=audio_codec,
                audio_channels=audio_channels,
                quality_score=quality_score,
                metadata=metadata,
                hdr_support=hdr_support,
                color_depth=color_depth,
                color_space=color_space
            )
            
        except Exception as e:
            logger.warning(f"FFprobe analysis failed: {e}")
            return None
    
    async def _analyze_with_opencv(self, file_path: Path) -> Optional[VideoFormatInfo]:
        """Analyze video with OpenCV (fallback method)"""
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                return None
            
            # Get basic properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Determine format from extension
            format_type = self._get_format_from_extension(file_path.suffix.lower().lstrip('.'))
            
            # Basic codec detection
            codec = VideoCodec.H264  # Default assumption
            
            file_size = file_path.stat().st_size
            bitrate = int((file_size * 8) / duration / 1000) if duration > 0 else 0
            
            return VideoFormatInfo(
                format_type=format_type or VideoFormat.MP4,
                codec=codec,
                resolution=(width, height),
                fps=fps,
                duration=duration,
                bitrate=bitrate,
                file_size=file_size,
                audio_codec=None,
                audio_channels=0,
                quality_score=0.5,  # Default score
                metadata={},
                hdr_support=False,
                color_depth=8,
                color_space='yuv420p'
            )
            
        except Exception as e:
            logger.warning(f"OpenCV analysis failed: {e}")
            return None
    
    async def _basic_format_detection(self, file_path: Path) -> VideoFormatInfo:
        """Basic format detection from file extension"""
        extension = file_path.suffix.lower().lstrip('.')
        format_type = self._get_format_from_extension(extension)
        
        if not format_type:
            format_type = VideoFormat.MP4  # Default
        
        file_size = file_path.stat().st_size
        
        return VideoFormatInfo(
            format_type=format_type,
            codec=VideoCodec.H264,
            resolution=(1920, 1080),  # Default assumption
            fps=30.0,
            duration=0.0,
            bitrate=0,
            file_size=file_size,
            audio_codec=None,
            audio_channels=0,
            quality_score=0.0,
            metadata={},
            hdr_support=False,
            color_depth=8,
            color_space='yuv420p'
        )
    
    def _map_container_to_format(self, container: str) -> VideoFormat:
        """Map container format to VideoFormat enum"""
        container_map = {
            'mp4': VideoFormat.MP4,
            'webm': VideoFormat.WEBM,
            'matroska': VideoFormat.MKV,
            'mov': VideoFormat.MOV,
            'avi': VideoFormat.AVI,
            'flv': VideoFormat.FLV,
            'asf': VideoFormat.WMV,
            'mpeg': VideoFormat.MPEG,
            'mpegts': VideoFormat.TS
        }
        return container_map.get(container.lower(), VideoFormat.MP4)
    
    def _map_codec_name(self, codec_name: str) -> VideoCodec:
        """Map codec name to VideoCodec enum"""
        codec_map = {
            'h264': VideoCodec.H264,
            'h265': VideoCodec.H265,
            'hevc': VideoCodec.H265,
            'av1': VideoCodec.AV1,
            'vp8': VideoCodec.VP8,
            'vp9': VideoCodec.VP9,
            'mpeg4': VideoCodec.MPEG4,
            'mpeg2video': VideoCodec.MPEG2,
            'prores': VideoCodec.PRORES
        }
        return codec_map.get(codec_name.lower(), VideoCodec.H264)
    
    def _get_format_from_extension(self, extension: str) -> Optional[VideoFormat]:
        """Get format from file extension"""
        ext_map = {
            'mp4': VideoFormat.MP4,
            'webm': VideoFormat.WEBM,
            'mkv': VideoFormat.MKV,
            'mov': VideoFormat.MOV,
            'avi': VideoFormat.AVI,
            'flv': VideoFormat.FLV,
            'wmv': VideoFormat.WMV,
            'mpeg': VideoFormat.MPEG,
            'mpg': VideoFormat.MPEG,
            'ts': VideoFormat.TS
        }
        return ext_map.get(extension)
    
    def _extract_color_depth(self, video_stream: Dict[str, Any]) -> int:
        """Extract color depth from video stream"""
        bits_per_raw_sample = video_stream.get('bits_per_raw_sample')
        if bits_per_raw_sample:
            return int(bits_per_raw_sample)
        
        # Try to determine from pixel format
        pix_fmt = video_stream.get('pix_fmt', '')
        if '10' in pix_fmt:
            return 10
        elif '12' in pix_fmt:
            return 12
        else:
            return 8  # Default
    
    def _detect_hdr_support(self, video_stream: Dict[str, Any]) -> bool:
        """Detect HDR support in video stream"""
        # Check color transfer characteristics
        color_trc = video_stream.get('color_trc', '')
        hdr_transfers = ['smpte2084', 'arib-std-b67', 'bt2020-10', 'bt2020-12']
        
        if any(hdr_trc in color_trc for hdr_trc in hdr_transfers):
            return True
        
        # Check color primaries
        color_primaries = video_stream.get('color_primaries', '')
        if 'bt2020' in color_primaries:
            return True
        
        # Check bit depth
        if self._extract_color_depth(video_stream) > 8:
            return True
        
        return False
    
    async def _analyze_video_quality(self, file_path: Path, 
                                   video_stream: Dict[str, Any]) -> float:
        """Analyze video quality using AI"""
        try:
            # Use quality analyzer for comprehensive assessment
            quality_score = await self.quality_analyzer.analyze_video_quality(
                str(file_path), sample_duration=5.0
            )
            return quality_score
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return 0.5  # Default score
    
    async def convert_format(self, input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           options: VideoProcessingOptions) -> VideoFormatInfo:
        """Convert video format with optimization"""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Detect input format
            input_info = await self.detect_format(input_path)
            
            # Build FFmpeg command
            ffmpeg_cmd = await self._build_ffmpeg_command(
                input_path, output_path, options, input_info
            )
            
            # Execute conversion
            await self._execute_ffmpeg_conversion(ffmpeg_cmd)
            
            # Return format info for converted file
            return await self.detect_format(output_path)
            
        except Exception as e:
            logger.error(f"Error converting video format: {e}")
            raise
    
    async def _build_ffmpeg_command(self, input_path: Path, output_path: Path,
                                  options: VideoProcessingOptions,
                                  input_info: VideoFormatInfo) -> str:
        """Build optimized FFmpeg command"""
        # Get optimal encoder
        encoder = self.codec_engine.get_optimal_encoder(
            options.target_codec, options.hardware_acceleration
        )
        
        # Base command
        cmd = f'ffmpeg -i "{input_path}"'
        
        # Video encoding options
        cmd += f' -c:v {encoder}'
        
        # Resolution scaling
        if options.target_resolution:
            width, height = options.target_resolution
            cmd += f' -s {width}x{height}'
        
        # Frame rate
        if options.target_fps:
            cmd += f' -r {options.target_fps}'
        
        # Bitrate
        if options.target_bitrate:
            cmd += f' -b:v {options.target_bitrate}k'
        else:
            # Calculate optimal bitrate
            resolution = options.target_resolution or input_info.resolution
            fps = options.target_fps or input_info.fps
            bitrate = self.codec_engine.calculate_optimal_bitrate(
                resolution, fps, options.quality_preset
            )
            cmd += f' -b:v {bitrate}k'
        
        # Audio options
        if options.preserve_audio and input_info.audio_codec:
            cmd += ' -c:a aac -b:a 128k'
        else:
            cmd += ' -an'  # No audio
        
        # Streaming optimization
        if options.optimize_for_streaming:
            cmd += ' -movflags +faststart'  # For MP4
            cmd += ' -preset medium'  # Balance speed/quality
        
        # HDR options
        if options.enable_hdr and input_info.hdr_support:
            cmd += ' -color_primaries bt2020'
            cmd += ' -color_trc smpte2084'
            cmd += ' -colorspace bt2020nc'
        
        # Output file
        cmd += f' "{output_path}"'
        
        # Overwrite output
        cmd += ' -y'
        
        return cmd
    
    async def _execute_ffmpeg_conversion(self, ffmpeg_cmd: str):
        """Execute FFmpeg conversion with progress tracking"""
        try:
            # Execute command using asyncio
            process = await asyncio.create_subprocess_shell(
                ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise Exception(f"FFmpeg conversion failed: {error_msg}")
            
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            raise
    
    async def get_format_capabilities(self, format_type: VideoFormat) -> Dict[str, Any]:
        """Get format capabilities and limitations"""
        capabilities = {
            VideoFormat.MP4: {
                'max_resolution': (7680, 4320),  # 8K
                'max_fps': 120,
                'hdr_support': True,
                'streaming_optimized': True,
                'compatible_codecs': [VideoCodec.H264, VideoCodec.H265, VideoCodec.AV1],
                'browser_support': ['Chrome', 'Firefox', 'Safari', 'Edge'],
                'platform_support': ['iOS', 'Android', 'Windows', 'macOS', 'Linux']
            },
            VideoFormat.WEBM: {
                'max_resolution': (7680, 4320),
                'max_fps': 60,
                'hdr_support': True,
                'streaming_optimized': True,
                'compatible_codecs': [VideoCodec.VP8, VideoCodec.VP9, VideoCodec.AV1],
                'browser_support': ['Chrome', 'Firefox', 'Edge'],
                'platform_support': ['Android', 'Linux', 'Windows']
            },
            VideoFormat.MKV: {
                'max_resolution': (7680, 4320),
                'max_fps': 120,
                'hdr_support': True,
                'streaming_optimized': False,
                'compatible_codecs': [VideoCodec.H264, VideoCodec.H265, VideoCodec.AV1, VideoCodec.VP9],
                'browser_support': [],
                'platform_support': ['Windows', 'macOS', 'Linux']
            }
        }
        
        return capabilities.get(format_type, {})
    
    async def validate_video_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Comprehensive video file validation"""
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'format_info': None,
            'quality_assessment': None,
            'streaming_readiness': None
        }
        
        try:
            file_path = Path(file_path)
            
            # Check file exists and size
            if not file_path.exists():
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            if file_path.stat().st_size == 0:
                validation_result['errors'].append("File is empty")
                return validation_result
            
            # Detect and validate format
            format_info = await self.detect_format(file_path)
            validation_result['format_info'] = format_info
            
            # Validate video properties
            if format_info.resolution[0] < 1 or format_info.resolution[1] < 1:
                validation_result['errors'].append("Invalid video resolution")
            
            if format_info.fps <= 0:
                validation_result['warnings'].append("Invalid or missing frame rate")
            
            if format_info.duration <= 0:
                validation_result['warnings'].append("Invalid or missing duration")
            
            # Quality assessment
            quality_assessment = await self._comprehensive_quality_check(file_path)
            validation_result['quality_assessment'] = quality_assessment
            
            # Streaming readiness check
            streaming_check = await self._check_streaming_readiness(file_path, format_info)
            validation_result['streaming_readiness'] = streaming_check
            
            # Set validity based on errors
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Validation failed: {e}")
        
        return validation_result
    
    async def _comprehensive_quality_check(self, file_path: Path) -> Dict[str, Any]:
        """Perform comprehensive quality assessment"""
        try:
            quality_result = await self.quality_analyzer.comprehensive_analysis(
                str(file_path)
            )
            return quality_result
        except Exception as e:
            logger.warning(f"Quality check failed: {e}")
            return {'overall_score': 0.5, 'details': {}}
    
    async def _check_streaming_readiness(self, file_path: Path, 
                                       format_info: VideoFormatInfo) -> Dict[str, Any]:
        """Check if video is optimized for streaming"""
        readiness = {
            'is_ready': False,
            'optimizations_needed': [],
            'recommended_settings': {}
        }
        
        # Check format compatibility
        streaming_formats = [VideoFormat.MP4, VideoFormat.WEBM]
        if format_info.format_type not in streaming_formats:
            readiness['optimizations_needed'].append("Convert to streaming-friendly format")
            readiness['recommended_settings']['format'] = VideoFormat.MP4
        
        # Check codec compatibility
        streaming_codecs = [VideoCodec.H264, VideoCodec.H265, VideoCodec.VP9, VideoCodec.AV1]
        if format_info.codec not in streaming_codecs:
            readiness['optimizations_needed'].append("Use streaming-compatible codec")
            readiness['recommended_settings']['codec'] = VideoCodec.H264
        
        # Check resolution for adaptive streaming
        width, height = format_info.resolution
        if width > 1920 or height > 1080:
            readiness['optimizations_needed'].append("Consider multiple resolution variants")
        
        # Check bitrate for streaming
        if format_info.bitrate and format_info.bitrate > 10000:  # > 10 Mbps
            readiness['optimizations_needed'].append("Reduce bitrate for streaming")
            readiness['recommended_settings']['bitrate'] = 5000
        
        # Check faststart flag for MP4
        if format_info.format_type == VideoFormat.MP4:
            # This would require more detailed analysis of MP4 structure
            pass
        
        readiness['is_ready'] = len(readiness['optimizations_needed']) == 0
        
        return readiness

# Module exports for enterprise integration
__all__ = [
    'VideoFormatProcessor',
    'VideoCodecEngine',
    'VideoFormat',
    'VideoCodec', 
    'VideoQuality',
    'VideoFormatInfo',
    'VideoProcessingOptions'
]