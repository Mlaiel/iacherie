"""Video Transformer - Professional video processing for IA Influencer Agent Platform
===================================================================================

Advanced video transformation, conversion, and enhancement capabilities
for creators' video content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time
import subprocess
import numpy as np

try:
    import cv2
    import imageio
    from moviepy.editor import VideoFileClip, ImageSequenceClip
    VIDEO_LIBS_AVAILABLE = True
except ImportError:
    VIDEO_LIBS_AVAILABLE = False
    logging.warning("Video processing libraries not available. Some features may be limited.")

logger = logging.getLogger(__name__)


class VideoFormat(Enum):
    """Supported video formats."""

    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    WMV = "wmv"
    FLV = "flv"
    M4V = "m4v"


class VideoQuality(Enum):
    """Video quality presets."""

    LOW = "low"          # 480p, low bitrate
    MEDIUM = "medium"    # 720p, medium bitrate
    HIGH = "high"        # 1080p, high bitrate
    ULTRA = "ultra"      # 1440p/4K, ultra bitrate
    LOSSLESS = "lossless"  # Original quality
    CUSTOM = "custom"    # Custom settings


class VideoCodec(Enum):
    """Video codecs."""

    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    PRORES = "prores"
    MPEG4 = "mpeg4"


class VideoProfile(Enum):
    """Video encoding profiles."""

    BASELINE = "baseline"
    MAIN = "main"
    HIGH = "high"
    HIGH444 = "high444p"


@dataclass
class VideoSettings:
    """Video processing settings."""
    format: VideoFormat = VideoFormat.MP4
    quality: VideoQuality = VideoQuality.HIGH
    codec: Optional[VideoCodec] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    crf: Optional[int] = None  # Constant Rate Factor
    profile: Optional[VideoProfile] = None
    preset: Optional[str] = None  # Encoding speed preset
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    normalize_audio: bool = False
    stabilize: bool = False
    denoise: bool = False
    enhance_colors: bool = False
    sharpen: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    watermark: Optional[str] = None
    custom_filters: Optional[List[str]] = None


@dataclass
class VideoMetadata:
    """
Video file metadata."""
    title: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    size: Optional[int] = None
    format: Optional[str] = None
    creation_time: Optional[str] = None
    aspect_ratio: Optional[str] = None
    color_space: Optional[str] = None
    has_audio: bool = False
    has_video: bool = False


class VideoTransformer:
    """
    Professional video transformation engine for the IA Influencer Agent Platform.
    
    Provides advanced video processing, conversion, and enhancement capabilities
    optimized for creator content workflows.
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        config: Optional[Dict[str, Any]] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize video transformer.
        
        Args:
            enable_gpu: Enable GPU acceleration if available
            config: Configuration options
            temp_dir: Temporary directory for processing
        """
        self.enable_gpu = enable_gpu
        self.config = config or {}
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "video_transform"
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality presets
        self.quality_presets = {
            VideoQuality.LOW: {
                "width": 854, "height": 480, "bitrate": 1000, "crf": 28,
                "audio_bitrate": 128
            },
            VideoQuality.MEDIUM: {
                "width": 1280, "height": 720, "bitrate": 2500, "crf": 23,
                "audio_bitrate": 192
            },
            VideoQuality.HIGH: {
                "width": 1920, "height": 1080, "bitrate": 5000, "crf": 20,
                "audio_bitrate": 256
            },
            VideoQuality.ULTRA: {
                "width": 2560, "height": 1440, "bitrate": 10000, "crf": 18,
                "audio_bitrate": 320
            },
            VideoQuality.LOSSLESS: {
                "crf": 0, "audio_bitrate": 320
            }
        }
        
        # Codec mappings
        self.codec_mapping = {
            VideoFormat.MP4: VideoCodec.H264,
            VideoFormat.WEBM: VideoCodec.VP9,
            VideoFormat.MKV: VideoCodec.H265,
            VideoFormat.AVI: VideoCodec.MPEG4,
            VideoFormat.MOV: VideoCodec.H264,
        }
        
        # Check FFmpeg availability
        self.ffmpeg_available = self._check_ffmpeg()
        
        # Check for GPU acceleration
        self.gpu_available = self._check_gpu_acceleration() if enable_gpu else False
        
        logger.info(f"VideoTransformer initialized (GPU: {self.gpu_available}, FFmpeg: {self.ffmpeg_available})")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found. Video processing will be limited.")
            return False
    
    def _check_gpu_acceleration(self) -> bool:
        """Check for GPU acceleration support."""
        if not self.ffmpeg_available:
            return False
        
        try:
            # Check for NVIDIA GPU support
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True
            )
            
            encoders = result.stdout
            return "nvenc" in encoders or "cuda" in encoders
            
        except Exception:
            return False
    
    async def transform(self, request) -> Any:
        """
        Transform video based on request configuration.
        
        Args:
            request: Transformation request with video settings
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            # Parse request
            input_path = Path(request.input_path)
            settings = self._parse_video_settings(request)
            
            # Generate output path
            output_path = self._generate_output_path(input_path, settings, request.output_path)
            
            # Get input metadata
            input_metadata = await self.get_metadata(str(input_path))
            input_size = input_path.stat().st_size
            
            # Perform transformation
            result_path = await self._convert_video(input_path, output_path, settings)
            
            # Apply enhancements if requested
            if request.enhance_quality:
                result_path = await self._enhance_video(result_path, settings)
            
            # Get output metadata
            output_metadata = await self.get_metadata(str(result_path))
            output_size = result_path.stat().st_size
            
            # Calculate metrics
            compression_ratio = (input_size - output_size) / input_size if input_size > 0 else 0.0
            quality_score = await self._calculate_quality_score(str(input_path), str(result_path))
            
            return type('TransformationResult', (), {
                'success': True,
                'output_path': str(result_path),
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': compression_ratio,
                'quality_score': quality_score,
                'metadata': {
                    'input': input_metadata.__dict__,
                    'output': output_metadata.__dict__,
                    'settings': settings.__dict__
                },
                'processing_time': time.time() - start_time
            })()
            
        except Exception as e:
            logger.error(f"Video transformation failed: {str(e)}")
            return type('TransformationResult', (), {
                'success': False,
                'error_message': str(e),
                'processing_time': time.time() - start_time
            })()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: Union[str, VideoFormat] = VideoFormat.MP4,
        quality: Union[str, VideoQuality] = VideoQuality.HIGH,
        **kwargs
    ) -> bool:
        """
        Convert video file to specified format and quality.
        
        Args:
            input_path: Input video file path
            output_path: Output video file path
            format: Target video format
            quality: Output quality level
            **kwargs: Additional settings
            
        Returns:
            Success status
        """
        settings = VideoSettings(
            format=format if isinstance(format, VideoFormat) else VideoFormat(format),
            quality=quality if isinstance(quality, VideoQuality) else VideoQuality(quality),
            **kwargs
        )
        
        try:
            input_file = Path(input_path)
            output_file = Path(output_path)
            
            await self._convert_video(input_file, output_file, settings)
            return True
            
        except Exception as e:
            logger.error(f"Video conversion failed: {str(e)}")
            return False
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enhance video quality using AI and signal processing.
        
        Args:
            input_path: Input video file path
            output_path: Output video file path
            enhancement_options: Enhancement configuration
            
        Returns:
            Success status
        """
        try:
            options = enhancement_options or {}
            settings = VideoSettings(
                stabilize=options.get('stabilize', False),
                denoise=options.get('denoise', False),
                enhance_colors=options.get('enhance_colors', False),
                sharpen=options.get('sharpen', False)
            )
            
            input_file = Path(input_path)
            output_file = Path(output_path)
            
            await self._enhance_video(input_file, settings, output_file)
            return True
            
        except Exception as e:
            logger.error(f"Video enhancement failed: {str(e)}")
            return False
    
    async def get_metadata(self, file_path: str) -> VideoMetadata:
        """
        Extract comprehensive video metadata.
        
        Args:
            file_path: Video file path
            
        Returns:
            VideoMetadata object
        """
        try:
            metadata = VideoMetadata()
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return metadata
            
            metadata.size = file_path_obj.stat().st_size
            
            # Try FFprobe for detailed metadata
            if self.ffmpeg_available:
                try:
                    result = subprocess.run([
                        "ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_format", "-show_streams", file_path
                    ], capture_output=True, text=True, check=True)
                    
                    probe_data = json.loads(result.stdout)
                    format_info = probe_data.get("format", {})
                    streams = probe_data.get("streams", [])
                    
                    # Find video and audio streams
                    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
                    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
                    
                    # Extract format metadata
                    tags = format_info.get("tags", {})
                    metadata.title = tags.get("title")
                    metadata.creation_time = tags.get("creation_time")
                    metadata.duration = float(format_info.get("duration", 0))
                    metadata.bitrate = int(format_info.get("bit_rate", 0))
                    metadata.format = format_info.get("format_name")
                    
                    # Extract video metadata
                    if video_stream:
                        metadata.has_video = True
                        metadata.width = int(video_stream.get("width", 0))
                        metadata.height = int(video_stream.get("height", 0))
                        metadata.codec = video_stream.get("codec_name")
                        metadata.color_space = video_stream.get("color_space")
                        
                        # Calculate fps
                        fps_str = video_stream.get("r_frame_rate", "0/1")
                        if "/" in fps_str:
                            num, den = map(int, fps_str.split("/"))
                            metadata.fps = num / den if den > 0 else 0
                        
                        # Calculate aspect ratio
                        if metadata.width and metadata.height:
                            from fractions import Fraction
                            ratio = Fraction(metadata.width, metadata.height)
                            metadata.aspect_ratio = f"{ratio.numerator}:{ratio.denominator}"
                    
                    # Extract audio metadata
                    if audio_stream:
                        metadata.has_audio = True
                        metadata.audio_codec = audio_stream.get("codec_name")
                        metadata.audio_bitrate = int(audio_stream.get("bit_rate", 0))
                    
                except Exception as e:
                    logger.warning(f"Could not extract metadata with ffprobe: {e}")
            
            # Try with OpenCV/MoviePy as fallback
            if VIDEO_LIBS_AVAILABLE and not metadata.has_video:
                try:
                    cap = cv2.VideoCapture(file_path)
                    if cap.isOpened():
                        metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        metadata.fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        if metadata.fps > 0:
                            metadata.duration = frame_count / metadata.fps
                        metadata.has_video = True
                    cap.release()
                    
                except Exception as e:
                    logger.warning(f"Could not extract metadata with OpenCV: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return VideoMetadata()
    
    async def _convert_video(
        self,
        input_path: Path,
        output_path: Path,
        settings: VideoSettings
    ) -> Path:
        """Convert video with specified settings."""
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg required for video conversion")
        
        # Get quality settings
        quality_settings = self.quality_presets.get(settings.quality, {})
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", str(input_path)]
        
        # Video codec and settings
        codec = settings.codec or self.codec_mapping.get(settings.format, VideoCodec.H264)
        
        # GPU acceleration
        if self.gpu_available and codec == VideoCodec.H264:
            cmd.extend(["-c:v", "h264_nvenc"])
        elif self.gpu_available and codec == VideoCodec.H265:
            cmd.extend(["-c:v", "hevc_nvenc"])
        else:
            cmd.extend(["-c:v", codec.value])
        
        # Quality settings
        if settings.quality == VideoQuality.LOSSLESS:
            cmd.extend(["-crf", "0"])
        else:
            crf = settings.crf or quality_settings.get("crf", 23)
            cmd.extend(["-crf", str(crf)])
        
        # Resolution
        width = settings.width or quality_settings.get("width")
        height = settings.height or quality_settings.get("height")
        if width and height:
            cmd.extend(["-s", f"{width}x{height}"])
        
        # Frame rate
        if settings.fps:
            cmd.extend(["-r", str(settings.fps)])
        
        # Bitrate
        if settings.bitrate:
            cmd.extend(["-b:v", f"{settings.bitrate}k"])
        
        # Encoding profile and preset
        if settings.profile:
            cmd.extend(["-profile:v", settings.profile.value])
        
        if settings.preset:
            cmd.extend(["-preset", settings.preset])
        elif not self.gpu_available:
            cmd.extend(["-preset", "medium"])  # Balanced preset for CPU
        
        # Audio settings
        audio_codec = settings.audio_codec or "aac"
        cmd.extend(["-c:a", audio_codec])
        
        audio_bitrate = settings.audio_bitrate or quality_settings.get("audio_bitrate", 192)
        cmd.extend(["-b:a", f"{audio_bitrate}k"])
        
        # Video filters
        filters = []
        
        if settings.stabilize:
            filters.append("vidstabdetect=stepsize=6:shakiness=8:accuracy=9")
        
        if settings.denoise:
            filters.append("hqdn3d")
        
        if settings.enhance_colors:
            filters.append("eq=contrast=1.1:brightness=0.05:saturation=1.2")
        
        if settings.sharpen:
            filters.append("unsharp=5:5:1.0:5:5:0.0")
        
        if settings.fade_in > 0:
            filters.append(f"fade=t=in:st=0:d={settings.fade_in}")
        
        if settings.fade_out > 0:
            filters.append(f"fade=t=out:st={settings.fade_out}")
        
        if settings.watermark:
            filters.append(f"drawtext=text='{settings.watermark}':x=10:y=10:fontsize=24:fontcolor=white")
        
        if settings.custom_filters:
            filters.extend(settings.custom_filters)
        
        if filters:
            cmd.extend(["-vf", ",".join(filters)])
        
        # Audio filters
        audio_filters = []
        if settings.normalize_audio:
            audio_filters.append("loudnorm")
        
        if audio_filters:
            cmd.extend(["-af", ",".join(audio_filters)])
        
        # Output
        cmd.extend(["-y", str(output_path)])
        
        # Execute conversion
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {stderr.decode()}")
        
        return output_path
    
    async def _enhance_video(
        self,
        input_path: Path,
        settings: VideoSettings,
        output_path: Optional[Path] = None
    ) -> Path:
        """Enhance video quality using advanced processing."""
        if not output_path:
            output_path = input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
        
        try:
            # Build enhancement filters
            filters = []
            
            if settings.stabilize:
                # Two-pass stabilization
                vidstab_file = self.temp_dir / f"vidstab_{input_path.stem}.trf"
                
                # First pass: detect
                detect_cmd = [
                    "ffmpeg", "-i", str(input_path),
                    "-vf", f"vidstabdetect=stepsize=6:shakiness=8:accuracy=9:result={vidstab_file}",
                    "-f", "null", "-"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *detect_cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Second pass: transform
                filters.append(f"vidstabtransform=input={vidstab_file}:zoom=1:smoothing=30")
            
            if settings.denoise:
                filters.append("hqdn3d=4:3:6:4.5")
            
            if settings.enhance_colors:
                filters.append("eq=contrast=1.1:brightness=0.05:saturation=1.15:gamma=0.95")
            
            if settings.sharpen:
                filters.append("unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0")
            
            if not filters:
                # If no enhancement filters, just copy
                return input_path
            
            # Apply enhancement filters
            cmd = [
                "ffmpeg", "-i", str(input_path),
                "-vf", ",".join(filters),
                "-c:a", "copy",  # Copy audio without re-encoding
                "-y", str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"Video enhancement failed: {stderr.decode()}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Video enhancement failed: {str(e)}")
            return input_path
    
    async def _calculate_quality_score(self, input_path: str, output_path: str) -> Optional[float]:
        """Calculate video quality score comparing input and output."""
        try:
            if not VIDEO_LIBS_AVAILABLE:
                return None
            
            # Use SSIM (Structural Similarity Index) for quality comparison
            cap1 = cv2.VideoCapture(input_path)
            cap2 = cv2.VideoCapture(output_path)
            
            if not cap1.isOpened() or not cap2.isOpened():
                return None
            
            ssim_scores = []
            frame_count = 0
            max_frames = 30  # Sample frames for performance
            
            while frame_count < max_frames:
                ret1, frame1 = cap1.read()
                ret2, frame2 = cap2.read()
                
                if not ret1 or not ret2:
                    break
                
                # Convert to grayscale
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                
                # Resize to same dimensions if needed
                if gray1.shape != gray2.shape:
                    gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
                
                # Calculate SSIM
                from skimage.metrics import structural_similarity as ssim
                score = ssim(gray1, gray2)
                ssim_scores.append(score)
                
                frame_count += 1
            
            cap1.release()
            cap2.release()
            
            if ssim_scores:
                avg_ssim = np.mean(ssim_scores)
                return avg_ssim * 100  # Convert to percentage
            
            return None
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return None
    
    def _parse_video_settings(self, request) -> VideoSettings:
        """Parse transformation request into video settings."""
        settings = VideoSettings()
        
        if hasattr(request, 'target_format') and request.target_format:
            settings.format = VideoFormat(request.target_format)
        
        if hasattr(request, 'quality') and request.quality:
            if hasattr(request.quality, 'value'):
                settings.quality = VideoQuality(request.quality.value)
            else:
                settings.quality = VideoQuality(request.quality)
        
        if hasattr(request, 'options') and request.options:
            options = request.options
            settings.width = options.get('width')
            settings.height = options.get('height')
            settings.fps = options.get('fps')
            settings.bitrate = options.get('bitrate')
            settings.crf = options.get('crf')
            settings.preset = options.get('preset')
            settings.stabilize = options.get('stabilize', False)
            settings.denoise = options.get('denoise', False)
            settings.enhance_colors = options.get('enhance_colors', False)
            settings.sharpen = options.get('sharpen', False)
            settings.normalize_audio = options.get('normalize_audio', False)
            settings.fade_in = options.get('fade_in', 0.0)
            settings.fade_out = options.get('fade_out', 0.0)
            settings.watermark = options.get('watermark')
            settings.custom_filters = options.get('custom_filters')
            
            if options.get('codec'):
                settings.codec = VideoCodec(options['codec'])
            if options.get('profile'):
                settings.profile = VideoProfile(options['profile'])
        
        return settings
    
    def _generate_output_path(
        self,
        input_path: Path,
        settings: VideoSettings,
        requested_output: Optional[str] = None
    ) -> Path:
        """
Generate output file path."""
        if requested_output:
            return Path(requested_output)
        
        # Generate based on input and settings
        output_name = f"{input_path.stem}_{settings.quality.value}.{settings.format.value}"
        return input_path.parent / output_name
    
    async def cleanup(self):
        """Cleanup temporary files and resources."""
        try:
            # Clean temp directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("VideoTransformer cleanup completed")
            
        except Exception as e:
            logger.error(f"VideoTransformer cleanup failed: {str(e)}")


class VideoConverter:
    """Simplified video converter interface."""
    
    def __init__(self, transformer: Optional[VideoTransformer] = None):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def convert(
        self,
        input_path: str,
        output_path: str,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        quality: str = "high"
    ) -> bool:
        """Convert video file."""
        return await self.transformer.convert(input_path, output_path, format, quality)


class VideoEnhancer:
    """
Simplified video enhancer interface."""
    
    def __init__(self, transformer: Optional[VideoTransformer] = None):
        self.transformer = transformer or VideoTransformer()
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
Enhance video quality."""
        return await self.transformer.enhance(input_path, output_path, options)
