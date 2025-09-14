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
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

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