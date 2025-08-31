"""
Multimedia Content Optimization
Advanced optimization for multimedia content processing and enhancement

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer, Backend Senior Engineer, ML Engineer, 
              Database Administrator, Security Expert, Microservices Architect,
              Multimedia Processing Specialist, DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""

import asyncio
import logging
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import librosa
import soundfile as sf
import ffmpeg
from moviepy import VideoFileClip, AudioFileClip
from scipy import signal
from skimage import restoration, exposure, filters
import multiprocessing as mp

from .formats import (
    ContentFormat, AudioFormat, VideoFormat, ImageFormat, 
    SupportedFormats, QualityLevel, FormatSpecification
)
from .metadata_extractor import UniversalMetadataExtractor
from ..core.exceptions import OptimizationError, ProcessingError
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class OptimizationProfile:
    """Optimization profile configuration"""
    name: str
    description: str
    target_use: str  # 'web', 'mobile', 'print', 'archive', 'streaming', 'social'
    
    # Quality settings
    quality_level: QualityLevel = QualityLevel.HIGH
    preserve_aspect_ratio: bool = True
    enable_auto_enhancement: bool = True
    
    # Size optimization
    max_file_size: Optional[int] = None  # bytes
    target_compression: float = 0.8  # 0-1 scale
    
    # Resolution settings
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    maintain_quality: bool = True
    
    # Processing options
    parallel_processing: bool = True
    use_gpu_acceleration: bool = False
    cache_intermediate: bool = True
    
    # Format-specific settings
    audio_settings: Dict[str, Any] = field(default_factory=dict)
    video_settings: Dict[str, Any] = field(default_factory=dict)
    image_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of content optimization"""
    success: bool
    original_path: Path
    optimized_path: Optional[Path] = None
    
    # Size metrics
    original_size: int = 0
    optimized_size: int = 0
    size_reduction_bytes: int = 0
    size_reduction_percent: float = 0.0
    
    # Quality metrics
    quality_score: float = 0.0
    quality_preserved: bool = True
    visual_difference: float = 0.0
    
    # Processing metrics
    processing_time: float = 0.0
    operations_applied: List[str] = field(default_factory=list)
    
    # Technical details
    original_format: Optional[str] = None
    optimized_format: Optional[str] = None
    profile_used: Optional[str] = None
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Additional metrics
    metadata_preserved: bool = True
    optimization_ratio: float = 1.0
    technical_details: Dict[str, Any] = field(default_factory=dict)


class BaseOptimizer(ABC):
    """Abstract base class for content optimizers"""
    
    def __init__(self, profile: OptimizationProfile):
        self.profile = profile
        self.temp_dir = Path(tempfile.mkdtemp(prefix="multimedia_opt_"))
        self.metadata_extractor = UniversalMetadataExtractor()
        
    def __del__(self):
        """Cleanup temporary directory"""
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @abstractmethod
    async def optimize(self, content_path: Path, output_path: Optional[Path] = None) -> OptimizationResult:
        """Optimize content and return result"""
        pass
    
    @abstractmethod
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if optimizer supports format"""
        pass
    
    def _calculate_size_metrics(self, original_path: Path, optimized_path: Path) -> Tuple[int, int, float]:
        """Calculate size reduction metrics"""
        original_size = original_path.stat().st_size
        optimized_size = optimized_path.stat().st_size
        
        size_reduction = original_size - optimized_size
        reduction_percent = (size_reduction / original_size) * 100 if original_size > 0 else 0
        
        return size_reduction, reduction_percent, optimized_size
    
    async def _preserve_metadata(self, original_path: Path, optimized_path: Path):
        """Preserve important metadata from original to optimized file"""



        try:
            original_metadata = await self.metadata_extractor.extract_metadata(original_path)
            if original_metadata and hasattr(original_metadata, 'technical_metadata'):
                # Implementation depends on file format
                # This is a placeholder for format-specific metadata preservation
                pass
        except Exception as e:
            logger.warning(f"Could not preserve metadata: {str(e)}")


class AudioOptimizer(BaseOptimizer):
    """Professional audio content optimizer"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if optimizer supports audio format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.AUDIO
        return SupportedFormats.is_audio_format(format_type)
    
    async def optimize(self, content_path: Path, output_path: Optional[Path] = None) -> OptimizationResult:
        """Optimize audio content"""
        start_time = datetime.now()
        
        result = OptimizationResult(
            success=False,
            original_path=content_path,
            original_size=content_path.stat().st_size
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"optimized_{content_path.name}"
        
        try:
            # Load audio
            audio, sr = librosa.load(str(content_path), sr=None)
            result.original_format = content_path.suffix.lower().lstrip('.')
            
            # Apply optimizations
            optimized_audio = audio.copy()
            
            # Audio enhancement
            if self.profile.enable_auto_enhancement:
                optimized_audio = await self._enhance_audio(optimized_audio, sr, result)
            
            # Quality/compression optimization
            optimized_audio, target_sr = await self._optimize_audio_quality(
                optimized_audio, sr, result
            )
            
            # Dynamic range optimization
            optimized_audio = await self._optimize_dynamic_range(optimized_audio, result)
            
            # Format optimization
            output_format = await self._select_optimal_format(content_path, result)
            if output_format != result.original_format:
                output_path = output_path.with_suffix(f".{output_format}")
            
            # Save optimized audio
            await self._save_optimized_audio(
                optimized_audio, target_sr, output_path, output_format, result
            )
            
            # Calculate metrics
            size_reduction, reduction_percent, optimized_size = self._calculate_size_metrics(
                content_path, output_path
            )
            
            result.optimized_path = output_path
            result.optimized_size = optimized_size
            result.size_reduction_bytes = size_reduction
            result.size_reduction_percent = reduction_percent
            result.optimized_format = output_format
            result.success = True
            
            # Preserve metadata
            await self._preserve_metadata(content_path, output_path)
            
        except Exception as e:
            logger.error(f"Audio optimization failed: {str(e)}")
            result.errors.append(f"Optimization failed: {str(e)}")
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _enhance_audio(self, audio: np.ndarray, sr: int, 
                           result: OptimizationResult) -> np.ndarray:
        """Apply audio enhancement techniques"""
        enhanced_audio = audio.copy()
        
        try:
            # Noise reduction
            if self.profile.audio_settings.get('noise_reduction', True):
                # Spectral subtraction for noise reduction
                stft = librosa.stft(enhanced_audio)
                magnitude = np.abs(stft)
                phase = np.angle(stft)
                
                # Estimate noise from first 0.5 seconds
                noise_frames = int(0.5 * sr / (stft.shape[1] / len(audio)))
                noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
                
                # Apply spectral subtraction
                alpha = 2.0  # Over-subtraction factor
                clean_magnitude = magnitude - alpha * noise_spectrum
                clean_magnitude = np.maximum(clean_magnitude, 0.1 * magnitude)
                
                # Reconstruct audio
                enhanced_stft = clean_magnitude * np.exp(1j * phase)
                enhanced_audio = librosa.istft(enhanced_stft)
                result.operations_applied.append("noise_reduction")
            
            # Audio normalization
            if self.profile.audio_settings.get('normalize', True):
                peak = np.max(np.abs(enhanced_audio))
                if peak > 0:
                    target_peak = 0.95  # Leave some headroom
                    enhanced_audio = enhanced_audio * (target_peak / peak)
                result.operations_applied.append("normalization")
            
            # EQ enhancement (mild)
            if self.profile.audio_settings.get('eq_enhance', False):
                # Simple high-frequency enhancement
                nyquist = sr / 2
                high_freq = 3000  # 3kHz and above
                low_freq = 100    # Below 100Hz
                
                # High-pass filter to remove low-frequency noise
                sos_hp = signal.butter(2, low_freq/nyquist, btype='high', output='sos')
                enhanced_audio = signal.sosfilt(sos_hp, enhanced_audio)
                
                result.operations_applied.append("eq_enhancement")
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed: {str(e)}")
            result.warnings.append(f"Audio enhancement failed: {str(e)}")
            return audio
        
        return enhanced_audio
    
    async def _optimize_audio_quality(self, audio: np.ndarray, sr: int, 
                                    result: OptimizationResult) -> Tuple[np.ndarray, int]:
        """Optimize audio quality and sample rate"""
        target_sr = sr
        optimized_audio = audio.copy()
        
        # Target sample rates based on profile
        if self.profile.target_use == 'web':
            target_sr = 44100 if sr > 44100 else sr
        elif self.profile.target_use == 'mobile':
            target_sr = 22050 if sr > 22050 else sr
        elif self.profile.target_use == 'streaming':
            target_sr = 48000 if sr != 48000 else sr
        
        # Resample if necessary
        if target_sr != sr:
            optimized_audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            result.operations_applied.append(f"resample_{sr}_to_{target_sr}")
        
        # Bit depth optimization (conceptual - actual implementation depends on output format)
        if self.profile.audio_settings.get('optimize_bit_depth', True):
            # Ensure audio doesn't exceed reasonable dynamic range
            dynamic_range = np.max(optimized_audio) - np.min(optimized_audio)
            if dynamic_range > 0:
                # Scale to use available dynamic range efficiently
                optimized_audio = optimized_audio / dynamic_range
                result.operations_applied.append("bit_depth_optimization")
        
        return optimized_audio, target_sr
    
    async def _optimize_dynamic_range(self, audio: np.ndarray, 
                                    result: OptimizationResult) -> np.ndarray:
        """Optimize dynamic range for target use case"""
        if not self.profile.audio_settings.get('dynamic_range_compression', False):
            return audio
        
        try:
            # Simple compressor implementation
            threshold = 0.5  # Compression threshold
            ratio = 4.0      # Compression ratio
            
            # Find peaks above threshold
            peaks = np.abs(audio) > threshold
            
            if np.any(peaks):
                # Apply compression to peaks
                compressed_audio = audio.copy()
                compressed_audio[peaks] = np.sign(audio[peaks]) * (
                    threshold + (np.abs(audio[peaks]) - threshold) / ratio
                )
                
                # Smooth transitions
                compressed_audio = signal.savgol_filter(
                    compressed_audio, window_length=51, polyorder=3
                )
                
                result.operations_applied.append("dynamic_range_compression")
                return compressed_audio
        
        except Exception as e:
            logger.warning(f"Dynamic range optimization failed: {str(e)}")
            result.warnings.append(f"Dynamic range optimization failed: {str(e)}")
        
        return audio
    
    async def _select_optimal_format(self, original_path: Path, 
                                   result: OptimizationResult) -> str:
        """Select optimal audio format based on profile"""
        original_format = original_path.suffix.lower().lstrip('.')
        
        # Format selection based on use case
        if self.profile.target_use == 'web':
            return 'mp3'  # Good compression, universal support
        elif self.profile.target_use == 'mobile':
            return 'aac'  # Better compression than mp3
        elif self.profile.target_use == 'archive':
            return 'flac' # Lossless
        elif self.profile.target_use == 'streaming':
            return 'aac'  # Good for streaming
        
        # Default: keep original format if supported
        if original_format in ['mp3', 'aac', 'wav', 'flac', 'ogg']:
            return original_format
        
        return 'mp3'  # Fallback
    
    async def _save_optimized_audio(self, audio: np.ndarray, sr: int, 
                                  output_path: Path, output_format: str,
                                  result: OptimizationResult):
        """Save optimized audio to file"""



        try:
            if output_format in ['wav', 'flac']:
                # Lossless formats
                sf.write(str(output_path), audio, sr, subtype='PCM_16')
            else:
                # For compressed formats, save as WAV first then convert with ffmpeg
                temp_wav = self.temp_dir / "temp_audio.wav"
                sf.write(str(temp_wav), audio, sr, subtype='PCM_16')
                
                # Convert with ffmpeg
                quality_settings = self._get_ffmpeg_audio_settings(output_format)
                
                (
                    ffmpeg
                    .input(str(temp_wav))
                    .output(str(output_path), **quality_settings)
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                # Clean up
                temp_wav.unlink()
            
            result.operations_applied.append(f"save_as_{output_format}")
            
        except Exception as e:
            raise OptimizationError(f"Failed to save optimized audio: {str(e)}")
    
    def _get_ffmpeg_audio_settings(self, output_format: str) -> Dict[str, Any]:
        """Get ffmpeg settings for audio format"""
        base_settings = {}
        
        if output_format == 'mp3':
            if self.profile.quality_level == QualityLevel.HIGH:
                base_settings.update({'b:a': '320k'})
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                base_settings.update({'b:a': '192k'})
            else:
                base_settings.update({'b:a': '128k'})
        
        elif output_format == 'aac':
            if self.profile.quality_level == QualityLevel.HIGH:
                base_settings.update({'b:a': '256k'})
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                base_settings.update({'b:a': '128k'})
            else:
                base_settings.update({'b:a': '96k'})
        
        elif output_format == 'ogg':
            if self.profile.quality_level == QualityLevel.HIGH:
                base_settings.update({'q:a': '8'})
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                base_settings.update({'q:a': '6'})
            else:
                base_settings.update({'q:a': '4'})
        
        return base_settings


class VideoOptimizer(BaseOptimizer):
    """Professional video content optimizer"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if optimizer supports video format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.VIDEO
        return SupportedFormats.is_video_format(format_type)
    
    async def optimize(self, content_path: Path, output_path: Optional[Path] = None) -> OptimizationResult:
        """Optimize video content"""
        start_time = datetime.now()
        
        result = OptimizationResult(
            success=False,
            original_path=content_path,
            original_size=content_path.stat().st_size
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"optimized_{content_path.name}"
        
        try:
            # Load video for analysis
            video_clip = VideoFileClip(str(content_path))
            result.original_format = content_path.suffix.lower().lstrip('.')
            
            # Get video properties
            original_width, original_height = video_clip.size
            original_fps = video_clip.fps
            original_duration = video_clip.duration
            
            result.technical_details.update({
                'original_width': original_width,
                'original_height': original_height,
                'original_fps': original_fps,
                'original_duration': original_duration
            })
            
            # Determine optimal settings
            target_settings = await self._determine_target_settings(
                original_width, original_height, original_fps, result
            )
            
            # Select optimal format
            output_format = await self._select_optimal_format(content_path, result)
            if output_format != result.original_format:
                output_path = output_path.with_suffix(f".{output_format}")
            
            # Apply video optimizations with ffmpeg
            await self._optimize_with_ffmpeg(
                content_path, output_path, target_settings, output_format, result
            )
            
            # Calculate metrics
            size_reduction, reduction_percent, optimized_size = self._calculate_size_metrics(
                content_path, output_path
            )
            
            result.optimized_path = output_path
            result.optimized_size = optimized_size
            result.size_reduction_bytes = size_reduction
            result.size_reduction_percent = reduction_percent
            result.optimized_format = output_format
            result.success = True
            
            # Cleanup
            video_clip.close()
            
            # Preserve metadata
            await self._preserve_metadata(content_path, output_path)
            
        except Exception as e:
            logger.error(f"Video optimization failed: {str(e)}")
            result.errors.append(f"Optimization failed: {str(e)}")
            if 'video_clip' in locals():
                video_clip.close()
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _determine_target_settings(self, width: int, height: int, fps: float,
                                       result: OptimizationResult) -> Dict[str, Any]:
        """Determine optimal video settings"""
        settings = {}
        
        # Target resolution based on profile
        target_width, target_height = await self._calculate_target_resolution(
            width, height, result
        )
        
        if target_width != width or target_height != height:
            settings['scale'] = f"{target_width}:{target_height}"
            result.operations_applied.append(f"resize_{width}x{height}_to_{target_width}x{target_height}")
        
        # Target frame rate
        target_fps = await self._calculate_target_fps(fps, result)
        if abs(target_fps - fps) > 0.1:
            settings['fps'] = target_fps
            result.operations_applied.append(f"fps_change_{fps}_to_{target_fps}")
        
        # Bitrate calculation
        bitrate = await self._calculate_target_bitrate(
            target_width, target_height, target_fps, result
        )
        settings['bitrate'] = f"{bitrate}k"
        
        result.technical_details.update({
            'target_width': target_width,
            'target_height': target_height,
            'target_fps': target_fps,
            'target_bitrate': bitrate
        })
        
        return settings
    
    async def _calculate_target_resolution(self, width: int, height: int,
                                         result: OptimizationResult) -> Tuple[int, int]:
        """Calculate target resolution based on profile"""
        max_width = self.profile.max_width
        max_height = self.profile.max_height
        
        # Profile-specific defaults
        if self.profile.target_use == 'mobile':
            max_width = max_width or 720
            max_height = max_height or 480
        elif self.profile.target_use == 'web':
            max_width = max_width or 1280
            max_height = max_height or 720
        elif self.profile.target_use == 'social':
            max_width = max_width or 1080
            max_height = max_height or 1080
        elif self.profile.target_use == 'streaming':
            max_width = max_width or 1920
            max_height = max_height or 1080
        
        if not max_width and not max_height:
            return width, height
        
        # Calculate scaling
        if self.profile.preserve_aspect_ratio:
            # Maintain aspect ratio
            aspect_ratio = width / height
            
            if max_width and max_height:
                # Scale to fit within bounds
                scale_w = max_width / width
                scale_h = max_height / height
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale
                
                target_width = int(width * scale)
                target_height = int(height * scale)
            elif max_width:
                target_width = min(max_width, width)
                target_height = int(target_width / aspect_ratio)
            else:  # max_height
                target_height = min(max_height, height)
                target_width = int(target_height * aspect_ratio)
            
            # Ensure even dimensions (required for some codecs)
            target_width = target_width if target_width % 2 == 0 else target_width - 1
            target_height = target_height if target_height % 2 == 0 else target_height - 1
            
        else:
            # Allow aspect ratio change
            target_width = max_width if max_width else width
            target_height = max_height if max_height else height
        
        return target_width, target_height
    
    async def _calculate_target_fps(self, original_fps: float,
                                  result: OptimizationResult) -> float:
        """Calculate target frame rate"""
        
        # Profile-specific defaults
        if self.profile.target_use == 'mobile':
            max_fps = 30
        elif self.profile.target_use == 'web':
            max_fps = 30
        elif self.profile.target_use == 'social':
            max_fps = 60
        elif self.profile.target_use == 'streaming':
            max_fps = 60
        else:
            max_fps = original_fps
        
        # Don't exceed original fps
        target_fps = min(original_fps, max_fps)
        
        # Common frame rates
        common_fps = [24, 25, 30, 50, 60]
        
        # Find closest common frame rate
        for fps in common_fps:
            if abs(target_fps - fps) < 2:
                target_fps = fps
                break
        
        return target_fps
    
    async def _calculate_target_bitrate(self, width: int, height: int, fps: float,
                                      result: OptimizationResult) -> int:
        """Calculate target bitrate in kbps"""
        
        # Base bitrate calculation (simplified)
        pixels_per_second = width * height * fps
        
        # Bitrate factors based on quality level
        if self.profile.quality_level == QualityLevel.HIGH:
            bitrate_factor = 0.15
        elif self.profile.quality_level == QualityLevel.MEDIUM:
            bitrate_factor = 0.10
        else:  # LOW
            bitrate_factor = 0.07
        
        # Use case adjustments
        if self.profile.target_use == 'mobile':
            bitrate_factor *= 0.7  # Lower for mobile
        elif self.profile.target_use == 'social':
            bitrate_factor *= 0.8  # Optimized for social media
        elif self.profile.target_use == 'streaming':
            bitrate_factor *= 1.2  # Higher for streaming
        
        base_bitrate = int(pixels_per_second * bitrate_factor / 1000)  # Convert to kbps
        
        # Reasonable bounds
        min_bitrate = 500   # 500 kbps minimum
        max_bitrate = 10000 # 10 Mbps maximum
        
        target_bitrate = max(min_bitrate, min(base_bitrate, max_bitrate))
        
        return target_bitrate
    
    async def _select_optimal_format(self, original_path: Path,
                                   result: OptimizationResult) -> str:
        """Select optimal video format based on profile"""
        original_format = original_path.suffix.lower().lstrip('.')
        
        # Format selection based on use case
        if self.profile.target_use == 'web':
            return 'mp4'  # Universal web support
        elif self.profile.target_use == 'mobile':
            return 'mp4'  # Best mobile support
        elif self.profile.target_use == 'social':
            return 'mp4'  # Social media standard
        elif self.profile.target_use == 'streaming':
            return 'mp4'  # Streaming standard
        elif self.profile.target_use == 'archive':
            return original_format  # Preserve original format
        
        # Default: mp4 for its universal support
        return 'mp4'
    
    async def _optimize_with_ffmpeg(self, input_path: Path, output_path: Path,
                                  target_settings: Dict[str, Any], output_format: str,
                                  result: OptimizationResult):
        """Optimize video using ffmpeg"""
        
        # Build ffmpeg command
        input_stream = ffmpeg.input(str(input_path))
        
        # Video stream processing
        video_stream = input_stream['v']
        
        # Apply scaling if needed
        if 'scale' in target_settings:
            video_stream = ffmpeg.filter(video_stream, 'scale', target_settings['scale'])
        
        # Apply frame rate change if needed
        if 'fps' in target_settings:
            video_stream = ffmpeg.filter(video_stream, 'fps', fps=target_settings['fps'])
        
        # Audio stream (copy or optimize)
        audio_stream = input_stream['a']
        if self.profile.video_settings.get('optimize_audio', True):
            # Audio optimization settings
            audio_bitrate = self._get_audio_bitrate_for_video()
            audio_settings = {'b:a': f"{audio_bitrate}k"}
        else:
            # Copy audio stream
            audio_settings = {'c:a': 'copy'}
        
        # Video codec settings
        video_settings = self._get_video_codec_settings(output_format, target_settings)
        
        # Combine settings
        output_settings = {**video_settings, **audio_settings}
        
        # Build output
        output = ffmpeg.output(
            video_stream, audio_stream,
            str(output_path),
            **output_settings
        )
        
        try:
            # Run ffmpeg
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            result.operations_applied.append(f"ffmpeg_optimization")
            
        except Exception as e:
            raise OptimizationError(f"FFmpeg optimization failed: {str(e)}")
    
    def _get_video_codec_settings(self, output_format: str, 
                                 target_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Get video codec settings"""
        settings = {}
        
        if output_format == 'mp4':
            settings['c:v'] = 'libx264'
            settings['preset'] = 'medium'
            
            if self.profile.quality_level == QualityLevel.HIGH:
                settings['crf'] = '18'
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                settings['crf'] = '23'
            else:
                settings['crf'] = '28'
                
        elif output_format == 'webm':
            settings['c:v'] = 'libvpx-vp9'
            settings['crf'] = '30'
            settings['b:v'] = '0'  # Use CRF mode
            
        elif output_format == 'avi':
            settings['c:v'] = 'libx264'
            settings['crf'] = '23'
        
        # Add bitrate if specified
        if 'bitrate' in target_settings:
            settings['b:v'] = target_settings['bitrate']
            if 'crf' in settings:
                del settings['crf']  # Can't use both CRF and bitrate
        
        # Profile settings
        if output_format == 'mp4':
            if self.profile.target_use in ['mobile', 'web']:
                settings['profile:v'] = 'baseline'
                settings['level'] = '3.0'
            else:
                settings['profile:v'] = 'high'
                settings['level'] = '4.0'
        
        return settings
    
    def _get_audio_bitrate_for_video(self) -> int:
        """Get appropriate audio bitrate for video"""
        if self.profile.quality_level == QualityLevel.HIGH:
            return 192  # 192 kbps
        elif self.profile.quality_level == QualityLevel.MEDIUM:
            return 128  # 128 kbps
        else:
            return 96   # 96 kbps


class ImageOptimizer(BaseOptimizer):
    """Professional image content optimizer"""
    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if optimizer supports image format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.IMAGE
        return SupportedFormats.is_image_format(format_type)
    
    async def optimize(self, content_path: Path, output_path: Optional[Path] = None) -> OptimizationResult:
        """Optimize image content"""
        start_time = datetime.now()
        
        result = OptimizationResult(
            success=False,
            original_path=content_path,
            original_size=content_path.stat().st_size
        )
        
        if output_path is None:
            output_path = self.temp_dir / f"optimized_{content_path.name}"
        
        try:
            # Load image
            with Image.open(content_path) as image:
                original_image = image.copy()
                result.original_format = image.format.lower() if image.format else content_path.suffix.lower().lstrip('.')
                
                original_width, original_height = original_image.size
                result.technical_details.update({
                    'original_width': original_width,
                    'original_height': original_height,
                    'original_mode': original_image.mode
                })
                
                # Apply optimizations
                optimized_image = original_image.copy()
                
                # Size optimization
                if self.profile.max_width or self.profile.max_height:
                    optimized_image = await self._resize_image(optimized_image, result)
                
                # Quality enhancement
                if self.profile.enable_auto_enhancement:
                    optimized_image = await self._enhance_image(optimized_image, result)
                
                # Color optimization
                optimized_image = await self._optimize_colors(optimized_image, result)
                
                # Format optimization
                output_format = await self._select_optimal_format(content_path, result)
                if output_format != result.original_format:
                    output_path = output_path.with_suffix(f".{output_format}")
                
                # Save optimized image
                await self._save_optimized_image(
                    optimized_image, output_path, output_format, result
                )
                
                # Calculate metrics
                size_reduction, reduction_percent, optimized_size = self._calculate_size_metrics(
                    content_path, output_path
                )
                
                result.optimized_path = output_path
                result.optimized_size = optimized_size
                result.size_reduction_bytes = size_reduction
                result.size_reduction_percent = reduction_percent
                result.optimized_format = output_format
                result.success = True
                
                # Calculate visual difference
                result.visual_difference = await self._calculate_visual_difference(
                    original_image, optimized_image
                )
            
            # Preserve metadata
            await self._preserve_metadata(content_path, output_path)
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            result.errors.append(f"Optimization failed: {str(e)}")
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _resize_image(self, image: Image.Image, 
                          result: OptimizationResult) -> Image.Image:
        """Resize image based on profile settings"""
        original_width, original_height = image.size
        
        # Calculate target size
        target_width, target_height = await self._calculate_target_size(
            original_width, original_height, result
        )
        
        if target_width == original_width and target_height == original_height:
            return image
        
        # Choose resampling algorithm based on quality level
        if self.profile.quality_level == QualityLevel.HIGH:
            resample = Image.Resampling.LANCZOS
        elif self.profile.quality_level == QualityLevel.MEDIUM:
            resample = Image.Resampling.BILINEAR
        else:
            resample = Image.Resampling.NEAREST
        
        # Resize image
        resized_image = image.resize((target_width, target_height), resample)
        
        result.operations_applied.append(f"resize_{original_width}x{original_height}_to_{target_width}x{target_height}")
        result.technical_details.update({
            'target_width': target_width,
            'target_height': target_height
        })
        
        return resized_image
    
    async def _calculate_target_size(self, width: int, height: int,
                                   result: OptimizationResult) -> Tuple[int, int]:
        """Calculate target image size"""
        max_width = self.profile.max_width
        max_height = self.profile.max_height
        
        # Profile-specific defaults
        if self.profile.target_use == 'web':
            max_width = max_width or 1920
            max_height = max_height or 1080
        elif self.profile.target_use == 'mobile':
            max_width = max_width or 800
            max_height = max_height or 600
        elif self.profile.target_use == 'social':
            # Keep original size for social media (they have their own compression)
            max_width = max_width or width
            max_height = max_height or height
        elif self.profile.target_use == 'print':
            # High resolution for print
            max_width = max_width or 3000
            max_height = max_height or 3000
        
        if not max_width and not max_height:
            return width, height
        
        if self.profile.preserve_aspect_ratio:
            # Maintain aspect ratio
            aspect_ratio = width / height
            
            if max_width and max_height:
                # Scale to fit within bounds
                scale_w = max_width / width
                scale_h = max_height / height
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale unless specified
                
                target_width = int(width * scale)
                target_height = int(height * scale)
            elif max_width:
                target_width = min(max_width, width)
                target_height = int(target_width / aspect_ratio)
            else:  # max_height
                target_height = min(max_height, height)
                target_width = int(target_height * aspect_ratio)
        else:
            # Allow aspect ratio change
            target_width = max_width if max_width else width
            target_height = max_height if max_height else height
        
        return max(1, target_width), max(1, target_height)
    
    async def _enhance_image(self, image: Image.Image,
                           result: OptimizationResult) -> Image.Image:
        """Apply image enhancement techniques"""
        enhanced_image = image.copy()
        
        try:
            # Convert to numpy for advanced processing
            img_array = np.array(enhanced_image)
            
            # Auto levels adjustment
            if self.profile.image_settings.get('auto_levels', True):
                # Histogram equalization for better contrast
                if len(img_array.shape) == 3:  # Color image
                    # Convert to LAB color space for better contrast adjustment
                    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
                    lab[:,:,0] = cv2.equalizeHist(lab[:,:,0])
                    img_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
                else:  # Grayscale
                    img_array = cv2.equalizeHist(img_array)
                
                result.operations_applied.append("auto_levels")
            
            # Noise reduction
            if self.profile.image_settings.get('noise_reduction', True):
                if len(img_array.shape) == 3:  # Color image
                    img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
                else:  # Grayscale
                    img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
                
                result.operations_applied.append("noise_reduction")
            
            # Sharpening
            if self.profile.image_settings.get('sharpen', False):
                # Unsharp masking
                gaussian = cv2.GaussianBlur(img_array, (0, 0), 2.0)
                img_array = cv2.addWeighted(img_array, 1.5, gaussian, -0.5, 0)
                
                result.operations_applied.append("sharpening")
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {str(e)}")
            result.warnings.append(f"Image enhancement failed: {str(e)}")
            return image
        
        return enhanced_image
    
    async def _optimize_colors(self, image: Image.Image,
                             result: OptimizationResult) -> Image.Image:
        """Optimize image colors"""
        optimized_image = image.copy()
        
        try:
            # Color mode optimization
            target_mode = await self._determine_optimal_color_mode(optimized_image, result)
            
            if optimized_image.mode != target_mode:
                if target_mode == 'P':
                    # Convert to palette mode for better compression
                    optimized_image = optimized_image.convert('P', palette=Image.ADAPTIVE, colors=256)
                elif target_mode == 'L':
                    # Convert to grayscale
                    optimized_image = optimized_image.convert('L')
                elif target_mode == 'RGB':
                    # Remove alpha channel if not needed
                    if optimized_image.mode in ['RGBA', 'LA']:
                        # Create white background
                        background = Image.new('RGB', optimized_image.size, (255, 255, 255))
                        background.paste(optimized_image, mask=optimized_image.split()[-1] if optimized_image.mode in ['RGBA', 'LA'] else None)
                        optimized_image = background
                
                result.operations_applied.append(f"color_mode_{image.mode}_to_{target_mode}")
                result.technical_details['target_mode'] = target_mode
        
        except Exception as e:
            logger.warning(f"Color optimization failed: {str(e)}")
            result.warnings.append(f"Color optimization failed: {str(e)}")
        
        return optimized_image
    
    async def _determine_optimal_color_mode(self, image: Image.Image,
                                          result: OptimizationResult) -> str:
        """Determine optimal color mode for the image"""
        
        # Analyze image content
        img_array = np.array(image)
        
        # Check if image is effectively grayscale
        if len(img_array.shape) == 3:
            # Check if all channels are similar (grayscale-like)
            r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
            if np.allclose(r, g, atol=5) and np.allclose(g, b, atol=5):
                return 'L'  # Grayscale
        
        # For small images or simple graphics, palette mode might be better
        if image.size[0] * image.size[1] < 100000:  # < 100k pixels
            unique_colors = len(set(tuple(pixel) for pixel in img_array.reshape(-1, img_array.shape[-1])))
            if unique_colors <= 256:
                return 'P'  # Palette mode
        
        # Check if alpha channel is actually used
        if image.mode in ['RGBA', 'LA']:
            if image.mode == 'RGBA':
                alpha = img_array[:,:,3]
            else:  # LA
                alpha = img_array[:,:,1]
            
            if np.all(alpha == 255):  # Fully opaque
                return 'RGB' if image.mode == 'RGBA' else 'L'
        
        # Default: keep current mode
        return image.mode
    
    async def _select_optimal_format(self, original_path: Path,
                                   result: OptimizationResult) -> str:
        """Select optimal image format"""
        original_format = original_path.suffix.lower().lstrip('.')
        
        # Get image properties
        target_mode = result.technical_details.get('target_mode', 'RGB')
        
        # Format selection based on use case and properties
        if self.profile.target_use == 'web':
            if target_mode in ['L', 'P'] or 'transparency' in result.technical_details:
                return 'png'
            else:
                return 'jpg'  # Better compression for photos
        
        elif self.profile.target_use == 'mobile':
            if target_mode in ['L', 'P']:
                return 'png'
            else:
                return 'jpg'
        
        elif self.profile.target_use == 'social':
            return 'jpg'  # Social media prefer JPEG
        
        elif self.profile.target_use == 'print':
            return 'tiff'  # High quality for print
        
        elif self.profile.target_use == 'archive':
            return original_format  # Preserve original
        
        # Default: JPEG for photos, PNG for graphics
        if target_mode in ['L', 'P']:
            return 'png'
        else:
            return 'jpg'
    
    async def _save_optimized_image(self, image: Image.Image, output_path: Path,
                                  output_format: str, result: OptimizationResult):
        """Save optimized image with format-specific settings"""
        
        save_kwargs = {}
        
        if output_format in ['jpg', 'jpeg']:
            # JPEG settings
            if self.profile.quality_level == QualityLevel.HIGH:
                save_kwargs['quality'] = 95
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                save_kwargs['quality'] = 85
            else:
                save_kwargs['quality'] = 75
            
            save_kwargs['optimize'] = True
            save_kwargs['progressive'] = True
            
        elif output_format == 'png':
            # PNG settings
            save_kwargs['optimize'] = True
            if self.profile.quality_level != QualityLevel.HIGH:
                save_kwargs['compress_level'] = 9  # Maximum compression
        
        elif output_format == 'webp':
            # WebP settings
            if self.profile.quality_level == QualityLevel.HIGH:
                save_kwargs['quality'] = 90
            elif self.profile.quality_level == QualityLevel.MEDIUM:
                save_kwargs['quality'] = 80
            else:
                save_kwargs['quality'] = 70
            
            save_kwargs['method'] = 6  # Higher compression
        
        # Save image
        image.save(str(output_path), format=output_format.upper(), **save_kwargs)
        
        result.operations_applied.append(f"save_as_{output_format}")
    
    async def _calculate_visual_difference(self, original: Image.Image,
                                         optimized: Image.Image) -> float:
        """Calculate visual difference between original and optimized image"""



        try:
            # Resize images to same size for comparison
            size = min(original.size, optimized.size)
            original_resized = original.resize(size, Image.Resampling.BILINEAR)
            optimized_resized = optimized.resize(size, Image.Resampling.BILINEAR)
            
            # Convert to same mode
            if original_resized.mode != optimized_resized.mode:
                if optimized_resized.mode == 'L':
                    original_resized = original_resized.convert('L')
                else:
                    optimized_resized = optimized_resized.convert(original_resized.mode)
            
            # Calculate MSE
            original_array = np.array(original_resized, dtype=np.float64)
            optimized_array = np.array(optimized_resized, dtype=np.float64)
            
            mse = np.mean((original_array - optimized_array) ** 2)
            
            # Normalize to 0-1 scale (255^2 is max possible MSE for 8-bit images)
            normalized_difference = mse / (255.0 ** 2)
            
            return float(normalized_difference)
            
        except Exception as e:
            logger.warning(f"Could not calculate visual difference: {str(e)}")
            return 0.0


class MediaOptimizer:
    """Universal multimedia content optimizer"""
    
    # Predefined optimization profiles
    OPTIMIZATION_PROFILES = {
        'web_standard': OptimizationProfile(
            name="Web Standard",
            description="Optimized for web delivery with good quality",
            target_use='web',
            quality_level=QualityLevel.MEDIUM,
            max_width=1920,
            max_height=1080,
            target_compression=0.8,
            audio_settings={'noise_reduction': True, 'normalize': True},
            video_settings={'optimize_audio': True},
            image_settings={'auto_levels': True, 'noise_reduction': True}
        ),
        
        'mobile_optimized': OptimizationProfile(
            name="Mobile Optimized",
            description="Optimized for mobile devices",
            target_use='mobile',
            quality_level=QualityLevel.MEDIUM,
            max_width=800,
            max_height=600,
            target_compression=0.7,
            audio_settings={'noise_reduction': True, 'normalize': True},
            video_settings={'optimize_audio': True},
            image_settings={'auto_levels': True, 'noise_reduction': True}
        ),
        
        'social_media': OptimizationProfile(
            name="Social Media",
            description="Optimized for social media platforms",
            target_use='social',
            quality_level=QualityLevel.MEDIUM,
            max_width=1080,
            max_height=1080,
            target_compression=0.75,
            audio_settings={'normalize': True, 'dynamic_range_compression': True},
            video_settings={'optimize_audio': True},
            image_settings={'auto_levels': True, 'sharpen': True}
        ),
        
        'high_quality': OptimizationProfile(
            name="High Quality",
            description="High quality with minimal compression",
            target_use='archive',
            quality_level=QualityLevel.HIGH,
            target_compression=0.9,
            enable_auto_enhancement=False,
            audio_settings={'normalize': False},
            video_settings={'optimize_audio': False},
            image_settings={'auto_levels': False}
        ),
        
        'streaming_ready': OptimizationProfile(
            name="Streaming Ready",
            description="Optimized for streaming platforms",
            target_use='streaming',
            quality_level=QualityLevel.HIGH,
            max_width=1920,
            max_height=1080,
            audio_settings={'normalize': True, 'noise_reduction': True},
            video_settings={'optimize_audio': True},
            image_settings={'auto_levels': True}
        )
    }
    
    def __init__(self, profile: Union[str, OptimizationProfile] = 'web_standard'):
        if isinstance(profile, str):
            if profile not in self.OPTIMIZATION_PROFILES:
                raise ValueError(f"Unknown optimization profile: {profile}")
            self.profile = self.OPTIMIZATION_PROFILES[profile]
        else:
            self.profile = profile
        
        self.optimizers = {
            ContentFormat.AUDIO: AudioOptimizer(self.profile),
            ContentFormat.VIDEO: VideoOptimizer(self.profile),
            ContentFormat.IMAGE: ImageOptimizer(self.profile)
        }
    
    async def optimize(self, content_path: Path, output_path: Optional[Path] = None,
                      content_type: Optional[Union[str, ContentFormat]] = None) -> OptimizationResult:
        """Optimize multimedia content"""
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content_path)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate optimizer
        optimizer = self.optimizers.get(content_type)
        if optimizer is None:
            return OptimizationResult(
                success=False,
                original_path=content_path,
                errors=[f"No optimizer available for content type: {content_type}"]
            )
        
        # Set profile info in result
        result = await optimizer.optimize(content_path, output_path)
        result.profile_used = self.profile.name
        
        return result
    
    def _detect_content_type(self, content_path: Path) -> ContentFormat:
        """Auto-detect content type from file extension"""
        extension = content_path.suffix.lower().lstrip('.')
        format_enum = SupportedFormats.get_format_by_extension(extension)
        
        if format_enum:
            if isinstance(format_enum, AudioFormat):
                return ContentFormat.AUDIO
            elif isinstance(format_enum, VideoFormat):
                return ContentFormat.VIDEO
            elif isinstance(format_enum, ImageFormat):
                return ContentFormat.IMAGE
        
        raise OptimizationError(f"Unable to detect content type for extension: {extension}")
    
    async def batch_optimize(self, content_paths: List[Path],
                           output_directory: Optional[Path] = None,
                           preserve_structure: bool = True) -> List[OptimizationResult]:
        """Optimize multiple multimedia files"""
        
        results = []
        
        if self.profile.parallel_processing:
            # Process files in parallel
            max_workers = min(mp.cpu_count(), len(content_paths))
            
            async def optimize_single(path):
                output_path = None
                if output_directory:
                    if preserve_structure:
                        # Preserve directory structure
                        rel_path = path.relative_to(path.parent)
                        output_path = output_directory / rel_path
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        output_path = output_directory / path.name
                
                return await self.optimize(path, output_path)
            
            # Create tasks
            tasks = [optimize_single(path) for path in content_paths]
            
            # Run with limited concurrency
            semaphore = asyncio.Semaphore(max_workers)
            
            async def run_with_semaphore(task):
                async with semaphore:
                    return await task
            
            limited_tasks = [run_with_semaphore(task) for task in tasks]
            results = await asyncio.gather(*limited_tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = OptimizationResult(
                        success=False,
                        original_path=content_paths[i],
                        errors=[f"Optimization exception: {str(result)}"]
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            return processed_results
        
        else:
            # Sequential processing
            for path in content_paths:
                output_path = None
                if output_directory:
                    if preserve_structure:
                        rel_path = path.relative_to(path.parent)
                        output_path = output_directory / rel_path
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        output_path = output_directory / path.name
                
                result = await self.optimize(path, output_path)
                results.append(result)
        
        return results
    
    def get_optimization_statistics(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Calculate optimization statistics"""
        stats = {
            'total_files': len(results),
            'successful_optimizations': sum(1 for r in results if r.success),
            'failed_optimizations': sum(1 for r in results if not r.success),
            'total_size_reduction_bytes': sum(r.size_reduction_bytes for r in results if r.success),
            'total_size_reduction_percent': 0.0,
            'average_size_reduction_percent': 0.0,
            'total_processing_time': sum(r.processing_time for r in results),
            'average_processing_time': 0.0,
            'average_quality_score': 0.0,
            'profile_used': self.profile.name,
            'content_type_distribution': {},
            'common_operations': {},
            'format_conversions': {}
        }
        
        if results:
            successful_results = [r for r in results if r.success]
            
            if successful_results:
                # Size reduction statistics
                original_total = sum(r.original_size for r in successful_results)
                if original_total > 0:
                    stats['total_size_reduction_percent'] = (
                        stats['total_size_reduction_bytes'] / original_total
                    ) * 100
                
                reduction_percentages = [r.size_reduction_percent for r in successful_results if r.size_reduction_percent > 0]
                if reduction_percentages:
                    stats['average_size_reduction_percent'] = sum(reduction_percentages) / len(reduction_percentages)
                
                # Quality scores
                quality_scores = [r.quality_score for r in successful_results if r.quality_score > 0]
                if quality_scores:
                    stats['average_quality_score'] = sum(quality_scores) / len(quality_scores)
            
            # Processing time
            stats['average_processing_time'] = stats['total_processing_time'] / len(results)
            
            # Content type distribution
            for result in results:
                content_type = self._detect_content_type(result.original_path).value
                stats['content_type_distribution'][content_type] = (
                    stats['content_type_distribution'].get(content_type, 0) + 1
                )
            
            # Common operations
            for result in results:
                for operation in result.operations_applied:
                    stats['common_operations'][operation] = (
                        stats['common_operations'].get(operation, 0) + 1
                    )
            
            # Format conversions
            for result in successful_results:
                if result.original_format and result.optimized_format:
                    if result.original_format != result.optimized_format:
                        conversion = f"{result.original_format} -> {result.optimized_format}"
                        stats['format_conversions'][conversion] = (
                            stats['format_conversions'].get(conversion, 0) + 1
                        )
        
        # Success rate
        stats['success_rate'] = (
            stats['successful_optimizations'] / stats['total_files']
            if stats['total_files'] > 0 else 0
        )
        
        return stats
    
    @classmethod
    def get_available_profiles(cls) -> List[str]:
        """Get list of available optimization profiles"""



        return list(cls.OPTIMIZATION_PROFILES.keys())
    
    @classmethod
    def create_custom_profile(cls, **kwargs) -> OptimizationProfile:
        """Create a custom optimization profile"""



        return OptimizationProfile(**kwargs)


# Convenience aliases and functions
MultimediaOptimizer = MediaOptimizer
ContentOptimizer = MediaOptimizer

async def optimize_multimedia(content_path: Path, profile: str = 'web_standard',
                             output_path: Optional[Path] = None) -> OptimizationResult:
    """Convenient function for single file optimization"""
    optimizer = MediaOptimizer(profile)
    return await optimizer.optimize(content_path, output_path)

async def batch_optimize_multimedia(content_paths: List[Path], profile: str = 'web_standard',
                                  output_directory: Optional[Path] = None) -> List[OptimizationResult]:
    """Convenient function for batch optimization"""
    optimizer = MediaOptimizer(profile)
    return await optimizer.batch_optimize(content_paths, output_directory)
