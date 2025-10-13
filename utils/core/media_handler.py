"""
Media Handler - Core Utilities Level 1
=====================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade media processing utility consolidating:
- Media processor (media_processor.py)
- Audio utilities (audio_utilities.py)
- Video utilities (video_utilities.py)

Performance: < 50ms per operation (media operations are I/O intensive)
Standards: 100% async, type hints, multimedia optimization
"""

import asyncio
import logging
import time
import mimetypes
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Union, Tuple, BinaryIO
)
from datetime import datetime, timezone
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import numpy as np

# Media processing imports with fallbacks
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MediaResult:
    """Enterprise result container for media processing operations."""
    success: bool
    result: Optional[Any] = None
    original_path: Optional[str] = None
    processed_path: Optional[str] = None
    media_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'result': self.result,
            'original_path': self.original_path,
            'processed_path': self.processed_path,
            'media_type': self.media_type,
            'metadata': self.metadata,
            'errors': self.errors,
            'warnings': self.warnings,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass
class ImageConfig:
    """Configuration for image processing operations."""
    max_width: int = 1920
    max_height: int = 1080
    quality: int = 85
    format: str = "JPEG"
    preserve_exif: bool = False

@dataclass
class AudioConfig:
    """Configuration for audio processing operations."""
    sample_rate: int = 44100
    channels: int = 2
    format: str = "wav"
    bitrate: str = "192k"

@dataclass
class VideoConfig:
    """Configuration for video processing operations."""
    width: int = 1280
    height: int = 720
    fps: int = 30
    codec: str = "h264"
    format: str = "mp4"
    crf: int = 23

class MediaHandler:
    """
    Enterprise media handler with ultra-high performance standards.
    
    Provides comprehensive media processing capabilities for images, 
    audio, and video with async operations and enterprise patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize media handler with enterprise configuration."""
        self.config = config or {}
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 50.0  # Higher for media operations
        self._max_file_size_mb = self.config.get('max_file_size_mb', 100)
        self._temp_dir = Path(self.config.get('temp_dir', '/tmp/media_processing'))
        
        # Supported formats
        self._image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self._audio_formats = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}
        self._video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        
        # Create temp directory
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        self._thread_pool.shutdown(wait=True)
        
    async def _measure_performance(self, operation: callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        
        if asyncio.iscoroutinefunction(operation):
            result = await operation()
        else:
            result = await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, operation
            )
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    def _validate_media_file(self, file_path: str) -> Tuple[bool, List[str], str]:
        """Validate media file security and format."""
        errors = []
        media_type = "unknown"
        
        path = Path(file_path)
        
        # Check file extension
        extension = path.suffix.lower()
        if extension in self._image_formats:
            media_type = "image"
        elif extension in self._audio_formats:
            media_type = "audio"
        elif extension in self._video_formats:
            media_type = "video"
        else:
            errors.append(f"Unsupported file format: {extension}")
        
        # Check file size
        try:
            file_size = path.stat().st_size
            if file_size > self._max_file_size_mb * 1024 * 1024:
                errors.append(f"File too large: {file_size} bytes")
        except OSError:
            errors.append(f"Cannot access file: {file_path}")
        
        return len(errors) == 0, errors, media_type
    
    # === IMAGE PROCESSING ===
    
    async def process_image(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        config: Optional[ImageConfig] = None
    ) -> MediaResult:
        """Process image with resize, optimization, and format conversion."""
        if not PIL_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["PIL (Pillow) not available for image processing"],
                media_type="image"
            )
        
        def _process_image():
            is_valid, validation_errors, media_type = self._validate_media_file(input_path)
            if not is_valid:
                return None, validation_errors
            
            if media_type != "image":
                return None, ["File is not a valid image"]
            
            img_config = config or ImageConfig()
            
            # Open and process image
            with Image.open(input_path) as img:
                original_size = img.size
                original_format = img.format
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if needed
                if (img.width > img_config.max_width or 
                    img.height > img_config.max_height):
                    img.thumbnail((img_config.max_width, img_config.max_height), 
                                Image.Resampling.LANCZOS)
                
                # Determine output path
                if not output_path:
                    input_path_obj = Path(input_path)
                    output_path = str(self._temp_dir / f"processed_{input_path_obj.stem}.{img_config.format.lower()}")
                
                # Save processed image
                save_kwargs = {
                    'format': img_config.format,
                    'quality': img_config.quality,
                    'optimize': True
                }
                
                if img_config.preserve_exif and hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        save_kwargs['exif'] = exif
                
                img.save(output_path, **save_kwargs)
                
                # Get processed image info
                processed_size = Path(output_path).stat().st_size
                
                return {
                    'output_path': output_path,
                    'original_size': original_size,
                    'processed_size': img.size,
                    'original_format': original_format,
                    'processed_format': img_config.format,
                    'file_size_reduction': Path(input_path).stat().st_size - processed_size,
                    'compression_ratio': processed_size / Path(input_path).stat().st_size
                }, []
        
        try:
            result, exec_time = await self._measure_performance(_process_image)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=input_path,
                    media_type="image"
                )
            
            data = result[0]
            return MediaResult(
                success=True,
                result=data,
                original_path=input_path,
                processed_path=data['output_path'],
                media_type="image",
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'process_image',
                    'original_size': data['original_size'],
                    'processed_size': data['processed_size'],
                    'file_size_reduction': data['file_size_reduction'],
                    'compression_ratio': data['compression_ratio']
                }
            )
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=input_path,
                media_type="image"
            )
    
    async def extract_image_metadata(self, image_path: str) -> MediaResult:
        """Extract comprehensive image metadata."""
        if not PIL_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["PIL (Pillow) not available for image processing"],
                media_type="image"
            )
        
        def _extract_metadata():
            is_valid, validation_errors, media_type = self._validate_media_file(image_path)
            if not is_valid:
                return None, validation_errors
            
            with Image.open(image_path) as img:
                metadata = {
                    'filename': Path(image_path).name,
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P'),
                    'file_size': Path(image_path).stat().st_size
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = {
                            str(k): str(v) for k, v in exif.items()
                        }
                
                # Calculate aspect ratio
                metadata['aspect_ratio'] = img.width / img.height
                
                # Estimate color count (approximate)
                if img.mode == 'P':
                    metadata['estimated_colors'] = len(img.getcolors())
                elif img.mode in ('RGB', 'RGBA'):
                    # Sample for performance
                    sample = img.resize((100, 100))
                    colors = sample.getcolors(maxcolors=256*256*256)
                    metadata['estimated_colors'] = len(colors) if colors else 'many'
                
                return metadata, []
        
        try:
            result, exec_time = await self._measure_performance(_extract_metadata)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=image_path,
                    media_type="image"
                )
            
            return MediaResult(
                success=True,
                result=result[0],
                original_path=image_path,
                media_type="image",
                execution_time_ms=exec_time,
                metadata={'operation': 'extract_image_metadata'}
            )
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=image_path,
                media_type="image"
            )
    
    # === AUDIO PROCESSING ===
    
    async def process_audio(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        config: Optional[AudioConfig] = None
    ) -> MediaResult:
        """Process audio with format conversion and optimization."""
        if not AUDIO_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["Audio processing libraries (librosa, soundfile) not available"],
                media_type="audio"
            )
        
        def _process_audio():
            is_valid, validation_errors, media_type = self._validate_media_file(input_path)
            if not is_valid:
                return None, validation_errors
            
            if media_type != "audio":
                return None, ["File is not a valid audio file"]
            
            audio_config = config or AudioConfig()
            
            # Load audio file
            audio_data, sample_rate = librosa.load(
                input_path, 
                sr=audio_config.sample_rate,
                mono=(audio_config.channels == 1)
            )
            
            # Convert to stereo if needed
            if audio_config.channels == 2 and len(audio_data.shape) == 1:
                audio_data = np.array([audio_data, audio_data])
            
            # Determine output path
            if not output_path:
                input_path_obj = Path(input_path)
                output_path = str(self._temp_dir / f"processed_{input_path_obj.stem}.{audio_config.format}")
            
            # Save processed audio
            sf.write(
                output_path, 
                audio_data.T if len(audio_data.shape) == 2 else audio_data,
                audio_config.sample_rate
            )
            
            # Get file stats
            original_size = Path(input_path).stat().st_size
            processed_size = Path(output_path).stat().st_size
            
            return {
                'output_path': output_path,
                'original_sample_rate': librosa.get_samplerate(input_path),
                'processed_sample_rate': audio_config.sample_rate,
                'duration_seconds': len(audio_data) / audio_config.sample_rate,
                'channels': audio_config.channels,
                'file_size_reduction': original_size - processed_size,
                'compression_ratio': processed_size / original_size
            }, []
        
        try:
            result, exec_time = await self._measure_performance(_process_audio)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=input_path,
                    media_type="audio"
                )
            
            data = result[0]
            return MediaResult(
                success=True,
                result=data,
                original_path=input_path,
                processed_path=data['output_path'],
                media_type="audio",
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'process_audio',
                    'duration_seconds': data['duration_seconds'],
                    'channels': data['channels'],
                    'sample_rate': data['processed_sample_rate']
                }
            )
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=input_path,
                media_type="audio"
            )
    
    async def extract_audio_features(self, audio_path: str) -> MediaResult:
        """Extract audio features for analysis."""
        if not AUDIO_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["Audio processing libraries not available"],
                media_type="audio"
            )
        
        def _extract_features():
            is_valid, validation_errors, media_type = self._validate_media_file(audio_path)
            if not is_valid:
                return None, validation_errors
            
            # Load audio
            audio_data, sample_rate = librosa.load(audio_path)
            
            # Extract features
            features = {
                'duration': len(audio_data) / sample_rate,
                'sample_rate': sample_rate,
                'total_samples': len(audio_data),
                'rms_energy': float(np.sqrt(np.mean(audio_data**2))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(audio_data))),
            }
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features['mfcc_mean'] = [float(x) for x in np.mean(mfccs, axis=1)]
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo_bpm'] = float(tempo)
            
            return features, []
        
        try:
            result, exec_time = await self._measure_performance(_extract_features)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=audio_path,
                    media_type="audio"
                )
            
            return MediaResult(
                success=True,
                result=result[0],
                original_path=audio_path,
                media_type="audio",
                execution_time_ms=exec_time,
                metadata={'operation': 'extract_audio_features'}
            )
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=audio_path,
                media_type="audio"
            )
    
    # === VIDEO PROCESSING ===
    
    async def process_video(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        config: Optional[VideoConfig] = None
    ) -> MediaResult:
        """Process video with encoding and optimization."""
        if not FFMPEG_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["FFmpeg not available for video processing"],
                media_type="video"
            )
        
        def _process_video():
            is_valid, validation_errors, media_type = self._validate_media_file(input_path)
            if not is_valid:
                return None, validation_errors
            
            if media_type != "video":
                return None, ["File is not a valid video file"]
            
            video_config = config or VideoConfig()
            
            # Determine output path
            if not output_path:
                input_path_obj = Path(input_path)
                output_path = str(self._temp_dir / f"processed_{input_path_obj.stem}.{video_config.format}")
            
            # Build FFmpeg stream
            stream = ffmpeg.input(input_path)
            
            # Apply video filters
            video_args = {
                'vcodec': video_config.codec,
                'crf': video_config.crf,
                'r': video_config.fps
            }
            
            # Resize if needed
            if video_config.width and video_config.height:
                stream = ffmpeg.filter(stream, 'scale', video_config.width, video_config.height)
            
            # Output stream
            stream = ffmpeg.output(stream, output_path, **video_args)
            
            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Get file stats
            original_size = Path(input_path).stat().st_size
            processed_size = Path(output_path).stat().st_size
            
            # Get video info
            probe = ffmpeg.probe(output_path)
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                'output_path': output_path,
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'fps': eval(video_stream['r_frame_rate']),
                'duration': float(video_stream['duration']),
                'codec': video_stream['codec_name'],
                'file_size_reduction': original_size - processed_size,
                'compression_ratio': processed_size / original_size
            }, []
        
        try:
            result, exec_time = await self._measure_performance(_process_video)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=input_path,
                    media_type="video"
                )
            
            data = result[0]
            return MediaResult(
                success=True,
                result=data,
                original_path=input_path,
                processed_path=data['output_path'],
                media_type="video",
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'process_video',
                    'resolution': f"{data['width']}x{data['height']}",
                    'duration': data['duration'],
                    'fps': data['fps']
                }
            )
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=input_path,
                media_type="video"
            )
    
    async def extract_video_metadata(self, video_path: str) -> MediaResult:
        """Extract comprehensive video metadata."""
        if not FFMPEG_AVAILABLE:
            return MediaResult(
                success=False,
                errors=["FFmpeg not available for video processing"],
                media_type="video"
            )
        
        def _extract_metadata():
            is_valid, validation_errors, media_type = self._validate_media_file(video_path)
            if not is_valid:
                return None, validation_errors
            
            # Get video metadata using ffprobe
            probe = ffmpeg.probe(video_path)
            
            metadata = {
                'filename': Path(video_path).name,
                'file_size': Path(video_path).stat().st_size,
                'format_name': probe['format']['format_name'],
                'duration': float(probe['format']['duration']),
                'bit_rate': int(probe['format']['bit_rate']),
                'streams': []
            }
            
            # Process each stream
            for stream in probe['streams']:
                stream_info = {
                    'codec_type': stream['codec_type'],
                    'codec_name': stream['codec_name']
                }
                
                if stream['codec_type'] == 'video':
                    stream_info.update({
                        'width': int(stream['width']),
                        'height': int(stream['height']),
                        'fps': eval(stream['r_frame_rate']),
                        'aspect_ratio': stream.get('display_aspect_ratio', 'N/A'),
                        'pix_fmt': stream.get('pix_fmt', 'N/A')
                    })
                elif stream['codec_type'] == 'audio':
                    stream_info.update({
                        'sample_rate': int(stream['sample_rate']),
                        'channels': int(stream['channels']),
                        'channel_layout': stream.get('channel_layout', 'N/A')
                    })
                
                metadata['streams'].append(stream_info)
            
            return metadata, []
        
        try:
            result, exec_time = await self._measure_performance(_extract_metadata)
            
            if result[0] is None:  # Error case
                return MediaResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    original_path=video_path,
                    media_type="video"
                )
            
            return MediaResult(
                success=True,
                result=result[0],
                original_path=video_path,
                media_type="video",
                execution_time_ms=exec_time,
                metadata={'operation': 'extract_video_metadata'}
            )
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                original_path=video_path,
                media_type="video"
            )
    
    # === UTILITY METHODS ===
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> MediaResult:
        """Clean up temporary files older than specified age."""
        try:
            cleaned_count = 0
            total_size_freed = 0
            current_time = datetime.now()
            
            for file_path in self._temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age.total_seconds() > max_age_hours * 3600:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_count += 1
                        total_size_freed += file_size
            
            return MediaResult(
                success=True,
                result={
                    'files_cleaned': cleaned_count,
                    'size_freed_bytes': total_size_freed,
                    'size_freed_mb': total_size_freed / (1024 * 1024)
                },
                metadata={'operation': 'cleanup_temp_files'}
            )
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'cleanup_temp_files'}
            )

# Enterprise factory pattern for media handler
class MediaHandlerFactory:
    """Factory for creating configured media handler instances."""
    
    @staticmethod
    def create_handler(config: Optional[Dict[str, Any]] = None) -> MediaHandler:
        """Create and configure media handler."""
        return MediaHandler(config)
    
    @staticmethod
    def create_optimized_handler(
        max_file_size_mb: int = 100,
        temp_dir: str = "/tmp/media_processing"
    ) -> MediaHandler:
        """Create media handler optimized for enterprise operations."""
        config = {
            'max_file_size_mb': max_file_size_mb,
            'temp_dir': temp_dir
        }
        return MediaHandler(config)

# === ENHANCED AUDIO/VIDEO UTILITIES ===
# Consolidated from audio_utilities.py and video_utilities.py

from enum import Enum

class VideoCodec(Enum):
    """Video codec types for enterprise video processing"""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"
    PRORES = "prores"
    DNX = "dnxhd"
    MJPEG = "mjpeg"
    MPEG2 = "mpeg2video"

class AudioCodec(Enum):
    """Audio codec types for enterprise audio processing"""
    AAC = "aac"
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    OGG = "ogg"
    OPUS = "opus"

@dataclass
class AudioMetadata:
    """Enhanced audio metadata structure"""
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    size_bytes: int
    codec: str = ""
    bitrate: int = 0
    peak_amplitude: float = 0.0
    rms_amplitude: float = 0.0

@dataclass
class VideoMetadata:
    """Enhanced video metadata structure"""
    duration: float
    width: int
    height: int
    fps: float
    format: str
    size_bytes: int
    codec: str = ""
    bitrate: int = 0
    aspect_ratio: str = ""
    color_space: str = ""

class EnterpriseAudioProcessor:
    """Enhanced audio processing consolidated from audio_utilities.py
    
    Audio Engineer: Professional audio processing with DSP, analysis, and optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
    
    async def process_audio(
        self,
        audio_data: bytes,
        operations: List[str],
        output_format: str = "wav"
    ) -> MediaResult:
        """Process audio with specified operations"""
        try:
            start_time = time.time()
            
            if not AUDIO_AVAILABLE:
                return MediaResult(
                    success=False,
                    errors=["Audio processing libraries not available"]
                )
            
            # Load audio data
            audio_array, sample_rate = await self._load_audio_data(audio_data)
            
            # Apply operations
            processed_audio = audio_array
            effects_applied = []
            
            for operation in operations:
                if operation == "normalize":
                    processed_audio = self._normalize_audio(processed_audio)
                    effects_applied.append("normalize")
                elif operation == "denoise":
                    processed_audio = self._denoise_audio(processed_audio, sample_rate)
                    effects_applied.append("denoise")
                elif operation == "eq_bass_boost":
                    processed_audio = self._eq_bass_boost(processed_audio, sample_rate)
                    effects_applied.append("eq_bass_boost")
                elif operation == "compress":
                    processed_audio = self._compress_audio(processed_audio)
                    effects_applied.append("compress")
            
            # Convert back to bytes
            output_data = await self._audio_to_bytes(processed_audio, sample_rate, output_format)
            
            # Generate metadata
            metadata = AudioMetadata(
                duration=len(processed_audio) / sample_rate,
                sample_rate=sample_rate,
                channels=1 if len(processed_audio.shape) == 1 else processed_audio.shape[1],
                bit_depth=16,  # Default for processed audio
                format=output_format,
                size_bytes=len(output_data),
                codec=output_format.upper(),
                peak_amplitude=float(np.max(np.abs(processed_audio))),
                rms_amplitude=float(np.sqrt(np.mean(processed_audio**2)))
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return MediaResult(
                success=True,
                result=output_data,
                metadata={
                    'operation': 'process_audio',
                    'effects_applied': effects_applied,
                    'audio_metadata': metadata.__dict__,
                    'execution_time_ms': execution_time
                }
            )
        
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'process_audio'}
            )
    
    async def _load_audio_data(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Load audio data from bytes"""
        import io
        audio_file = io.BytesIO(audio_data)
        audio_array, sample_rate = librosa.load(audio_file, sr=None)
        return audio_array, sample_rate
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95  # Leave some headroom
        return audio
    
    def _denoise_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        # This is a simplified denoising - in production use more sophisticated algorithms
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Simple spectral gating
        noise_floor = np.percentile(magnitude, 20)
        mask = magnitude > noise_floor * 2
        
        cleaned_magnitude = magnitude * mask
        cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
        
        return librosa.istft(cleaned_stft)
    
    def _eq_bass_boost(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply bass boost EQ"""
        # Simple bass boost using high-pass filter to isolate low frequencies
        from scipy import signal
        
        # Design a low-pass filter for bass frequencies
        nyquist = sample_rate // 2
        low_freq = 200  # Hz
        b, a = signal.butter(2, low_freq / nyquist, btype='low')
        
        # Filter the audio
        bass = signal.filtfilt(b, a, audio)
        
        # Boost bass and mix back
        boosted_bass = bass * 1.5
        return audio + boosted_bass * 0.3
    
    def _compress_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compressor
        threshold = 0.7
        ratio = 4.0
        
        compressed = np.copy(audio)
        over_threshold = np.abs(compressed) > threshold
        
        compressed[over_threshold] = (
            np.sign(compressed[over_threshold]) * 
            (threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio)
        )
        
        return compressed
    
    async def _audio_to_bytes(self, audio: np.ndarray, sample_rate: int, format: str) -> bytes:
        """Convert audio array to bytes"""
        import io
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format=format.upper())
        buffer.seek(0)
        return buffer.read()

class EnterpriseVideoProcessor:
    """Enhanced video processing consolidated from video_utilities.py
    
    Audio Engineer: Video processing with audio sync and multimedia optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._ffmpeg_path = self.config.get('ffmpeg_path', 'ffmpeg')
    
    async def process_video(
        self,
        video_path: str,
        operations: List[str],
        output_format: str = "mp4"
    ) -> MediaResult:
        """Process video with specified operations"""
        try:
            start_time = time.time()
            
            # Validate input file
            if not Path(video_path).exists():
                return MediaResult(
                    success=False,
                    errors=[f"Video file not found: {video_path}"]
                )
            
            # Extract metadata
            metadata = await self._extract_video_metadata(video_path)
            
            # Build FFmpeg command
            cmd = [self._ffmpeg_path, "-i", video_path]
            effects_applied = []
            
            for operation in operations:
                if operation == "compress":
                    cmd.extend(["-c:v", "libx264", "-crf", "23"])
                    effects_applied.append("compress")
                elif operation == "scale_720p":
                    cmd.extend(["-vf", "scale=1280:720"])
                    effects_applied.append("scale_720p")
                elif operation == "normalize_audio":
                    cmd.extend(["-af", "loudnorm"])
                    effects_applied.append("normalize_audio")
                elif operation == "stabilize":
                    cmd.extend(["-vf", "vidstabdetect,vidstabtransform"])
                    effects_applied.append("stabilize")
            
            # Output file
            output_path = f"/tmp/processed_video_{int(time.time())}.{output_format}"
            cmd.extend(["-y", output_path])  # -y to overwrite
            
            # Execute FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return MediaResult(
                    success=False,
                    errors=[f"FFmpeg error: {stderr.decode()}"]
                )
            
            # Read processed file
            async with aiofiles.open(output_path, 'rb') as f:
                processed_data = await f.read()
            
            # Cleanup
            Path(output_path).unlink(missing_ok=True)
            
            execution_time = (time.time() - start_time) * 1000
            
            return MediaResult(
                success=True,
                result=processed_data,
                metadata={
                    'operation': 'process_video',
                    'effects_applied': effects_applied,
                    'video_metadata': metadata.__dict__ if metadata else {},
                    'execution_time_ms': execution_time
                }
            )
        
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            return MediaResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'process_video'}
            )
    
    async def _extract_video_metadata(self, video_path: str) -> Optional[VideoMetadata]:
        """Extract video metadata using FFprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return None
            
            data = json.loads(stdout.decode())
            
            # Find video stream
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                return None
            
            format_info = data.get('format', {})
            
            return VideoMetadata(
                duration=float(format_info.get('duration', 0)),
                width=int(video_stream.get('width', 0)),
                height=int(video_stream.get('height', 0)),
                fps=eval(video_stream.get('r_frame_rate', '0/1')),
                format=format_info.get('format_name', ''),
                size_bytes=int(format_info.get('size', 0)),
                codec=video_stream.get('codec_name', ''),
                bitrate=int(format_info.get('bit_rate', 0)),
                aspect_ratio=video_stream.get('display_aspect_ratio', ''),
                color_space=video_stream.get('color_space', '')
            )
        
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")
            return None

# Export enhanced media processing utilities
__all__ = ['MediaHandler', 'MediaHandlerFactory', 'MediaResult', 'MediaType',
           'EnterpriseAudioProcessor', 'EnterpriseVideoProcessor', 
           'AudioMetadata', 'VideoMetadata', 'AudioCodec', 'VideoCodec']