"""
Content Adapters Enterprise

Industrial-grade content adaptation and optimization system for multi-platform distribution.
Provides AI-powered content transformation, format optimization, and platform-specific adaptation.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os

import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
import moviepy.editor as mp
from moviepy.video.fx import resize, crop, speedx
from moviepy.audio.fx import audio_fadein, audio_fadeout
import librosa
import soundfile as sf
from transformers import (
    AutoTokenizer, AutoModel, AutoProcessor, 
    BlipProcessor, BlipForConditionalGeneration,
    GPT2LMHeadModel, GPT2Tokenizer
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import torch
import torch.nn.functional as F
import aiohttp
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, Field, validator

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....core.exceptions import ContentAdaptationError, ProcessingError, ValidationError
from ....utils.encryption import encrypt_data, decrypt_data
from ....utils.monitoring import MetricsCollector, track_performance
from ....utils.media_processing import (
    MediaProcessor, VideoProcessor, AudioProcessor, ImageProcessor
)
from ....utils.ai_content import AIContentGenerator, ContentAnalyzer
from ....models.content import ContentModel, ContentVariantModel, MediaAssetModel
from ....models.user import UserModel
from .platform_manager import PlatformType


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.content_adapters")
from ....models.content import ContentModel, ContentType
from ....utils.file_utils import get_file_info, download_file, upload_file
from .platform_manager import PlatformType


logger = logging.getLogger(__name__)


class AdaptationQuality(str, Enum):
    """Quality levels for content adaptation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class ContentFormat(str, Enum):
    """Content format specifications"""
    SQUARE = "square"  # 1:1
    PORTRAIT = "portrait"  # 9:16
    LANDSCAPE = "landscape"  # 16:9
    STORY = "story"  # 9:16
    FEED = "feed"  # 4:5
    COVER = "cover"  # 16:9


@dataclass
class PlatformSpecs:
    """Platform-specific content specifications"""
    max_file_size: int  # bytes
    max_duration: Optional[int]  # seconds
    supported_formats: List[str]
    preferred_aspect_ratios: List[str]
    max_resolution: Optional[Tuple[int, int]]
    min_resolution: Optional[Tuple[int, int]]
    quality_requirements: AdaptationQuality
    audio_requirements: Optional[Dict[str, Any]]


@dataclass
class AdaptationResult:
    """Result of content adaptation process"""
    adapted_url: str
    original_url: str
    platform: PlatformType
    format_changes: List[str]
    quality_metrics: Dict[str, Any]
    file_size: int
    duration: Optional[float]
    success: bool
    error_message: Optional[str] = None


class BaseContentAdapter(ABC):
    """Base class for all content adapters"""
    
    def __init__(self, db: Session):
        self.db = db
        self.platform_specs = self._initialize_platform_specs()
        
    @abstractmethod
    async def adapt_content(
        self,
        content: ContentModel,
        platform: PlatformType,
        target_format: Optional[ContentFormat] = None,
        quality: AdaptationQuality = AdaptationQuality.HIGH
    ) -> AdaptationResult:
        """Adapt content for specific platform"""
        pass
    
    def _initialize_platform_specs(self) -> Dict[PlatformType, PlatformSpecs]:
        """Initialize platform-specific specifications"""
        return {
            PlatformType.YOUTUBE: PlatformSpecs(
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                max_duration=12 * 3600,  # 12 hours
                supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
                preferred_aspect_ratios=["16:9", "9:16", "1:1"],
                max_resolution=(7680, 4320),  # 8K
                min_resolution=(426, 240),  # 240p
                quality_requirements=AdaptationQuality.HIGH,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 128000,
                    "channels": 2
                }
            ),
            PlatformType.INSTAGRAM: PlatformSpecs(
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=60,  # 60 seconds for reels
                supported_formats=["mp4", "mov", "jpg", "jpeg", "png"],
                preferred_aspect_ratios=["1:1", "4:5", "9:16"],
                max_resolution=(1920, 1920),
                min_resolution=(600, 600),
                quality_requirements=AdaptationQuality.HIGH,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 128000,
                    "channels": 2
                }
            ),
            PlatformType.TIKTOK: PlatformSpecs(
                max_file_size=500 * 1024 * 1024,  # 500MB
                max_duration=180,  # 3 minutes
                supported_formats=["mp4", "mov", "webm"],
                preferred_aspect_ratios=["9:16"],
                max_resolution=(1080, 1920),
                min_resolution=(540, 960),
                quality_requirements=AdaptationQuality.MEDIUM,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 128000,
                    "channels": 2
                }
            ),
            PlatformType.TWITTER: PlatformSpecs(
                max_file_size=512 * 1024 * 1024,  # 512MB
                max_duration=140,  # 2 minutes 20 seconds
                supported_formats=["mp4", "mov", "jpg", "jpeg", "png", "gif"],
                preferred_aspect_ratios=["16:9", "1:1", "9:16"],
                max_resolution=(1920, 1200),
                min_resolution=(600, 335),
                quality_requirements=AdaptationQuality.MEDIUM,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 128000,
                    "channels": 2
                }
            ),
            PlatformType.SPOTIFY: PlatformSpecs(
                max_file_size=200 * 1024 * 1024,  # 200MB
                max_duration=None,  # No limit for podcasts
                supported_formats=["mp3", "wav", "flac", "m4a"],
                preferred_aspect_ratios=[],  # Audio only
                max_resolution=None,
                min_resolution=None,
                quality_requirements=AdaptationQuality.HIGH,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 320000,  # High quality for music
                    "channels": 2
                }
            ),
            PlatformType.LINKEDIN: PlatformSpecs(
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=600,  # 10 minutes
                supported_formats=["mp4", "mov", "jpg", "jpeg", "png"],
                preferred_aspect_ratios=["16:9", "1:1"],
                max_resolution=(1920, 1080),
                min_resolution=(600, 400),
                quality_requirements=AdaptationQuality.HIGH,
                audio_requirements={
                    "sample_rate": 44100,
                    "bitrate": 128000,
                    "channels": 2
                }
            )
        }
    
    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate aspect ratio from dimensions"""
        from math import gcd
        
        ratio_gcd = gcd(width, height)
        ratio_w = width // ratio_gcd
        ratio_h = height // ratio_gcd
        
        return f"{ratio_w}:{ratio_h}"
    
    def _calculate_target_dimensions(
        self,
        current_width: int,
        current_height: int,
        target_format: ContentFormat,
        platform_specs: PlatformSpecs
    ) -> Tuple[int, int]:
        """Calculate target dimensions for adaptation"""
        
        # Define target aspect ratios
        aspect_ratios = {
            ContentFormat.SQUARE: (1, 1),
            ContentFormat.PORTRAIT: (9, 16),
            ContentFormat.LANDSCAPE: (16, 9),
            ContentFormat.STORY: (9, 16),
            ContentFormat.FEED: (4, 5),
            ContentFormat.COVER: (16, 9)
        }
        
        target_ratio = aspect_ratios.get(target_format, (current_width, current_height))
        max_res = platform_specs.max_resolution
        
        # Calculate dimensions maintaining aspect ratio
        if max_res:
            max_width, max_height = max_res
            
            # Calculate based on target aspect ratio
            if target_ratio[0] / target_ratio[1] > max_width / max_height:
                # Width is limiting factor
                new_width = max_width
                new_height = int(max_width * target_ratio[1] / target_ratio[0])
            else:
                # Height is limiting factor
                new_height = max_height
                new_width = int(max_height * target_ratio[0] / target_ratio[1])
        else:
            # Use optimal dimensions for the format
            optimal_dimensions = {
                ContentFormat.SQUARE: (1080, 1080),
                ContentFormat.PORTRAIT: (1080, 1920),
                ContentFormat.LANDSCAPE: (1920, 1080),
                ContentFormat.STORY: (1080, 1920),
                ContentFormat.FEED: (1080, 1350),
                ContentFormat.COVER: (1920, 1080)
            }
            
            new_width, new_height = optimal_dimensions.get(
                target_format, (current_width, current_height)
            )
        
        return new_width, new_height


class AudioContentAdapter(BaseContentAdapter):
    """Adapter for audio content optimization"""
    
    async def adapt_content(
        self,
        content: ContentModel,
        platform: PlatformType,
        target_format: Optional[ContentFormat] = None,
        quality: AdaptationQuality = AdaptationQuality.HIGH
    ) -> AdaptationResult:
        """Adapt audio content for platform requirements"""
        try:
            platform_specs = self.platform_specs[platform]
            
            if not platform_specs.audio_requirements:
                raise ValueError(f"Platform {platform} doesn't support audio content")
            
            # Download original audio file
            original_file = await download_file(content.file_url)
            
            # Load audio with librosa
            audio_data, sample_rate = librosa.load(original_file, sr=None)
            
            # Get current audio properties
            duration = len(audio_data) / sample_rate
            current_bitrate = self._estimate_bitrate(original_file)
            
            format_changes = []
            
            # Apply platform-specific adaptations
            adapted_audio = audio_data
            adapted_sample_rate = sample_rate
            
            # Adjust sample rate
            target_sample_rate = platform_specs.audio_requirements["sample_rate"]
            if sample_rate != target_sample_rate:
                adapted_audio = librosa.resample(
                    adapted_audio, 
                    orig_sr=sample_rate,
                    target_sr=target_sample_rate
                )
                adapted_sample_rate = target_sample_rate
                format_changes.append(f"Sample rate: {sample_rate}Hz -> {target_sample_rate}Hz")
            
            # Adjust duration if needed
            max_duration = platform_specs.max_duration
            if max_duration and duration > max_duration:
                # Trim audio to max duration
                max_samples = int(max_duration * adapted_sample_rate)
                adapted_audio = adapted_audio[:max_samples]
                duration = max_duration
                format_changes.append(f"Duration trimmed to {max_duration}s")
            
            # Apply quality enhancements based on quality setting
            if quality in [AdaptationQuality.HIGH, AdaptationQuality.ULTRA]:
                adapted_audio = self._enhance_audio_quality(adapted_audio, quality)
                format_changes.append(f"Audio enhancement applied ({quality.value})")
            
            # Normalize audio levels
            adapted_audio = self._normalize_audio(adapted_audio)
            format_changes.append("Audio normalized")
            
            # Convert to stereo if required
            target_channels = platform_specs.audio_requirements["channels"]
            if target_channels == 2 and len(adapted_audio.shape) == 1:
                adapted_audio = np.stack([adapted_audio, adapted_audio])
                format_changes.append("Converted to stereo")
            
            # Save adapted audio
            output_format = self._determine_output_format(platform)
            output_file = f"adapted_audio_{content.id}_{platform.value}.{output_format}"
            
            # Write audio file
            sf.write(
                output_file,
                adapted_audio.T if len(adapted_audio.shape) > 1 else adapted_audio,
                adapted_sample_rate,
                format=output_format.upper()
            )
            
            # Upload adapted file
            adapted_url = await upload_file(output_file)
            
            # Calculate quality metrics
            final_file_size = len(open(output_file, 'rb').read())
            
            quality_metrics = {
                "sample_rate": adapted_sample_rate,
                "duration": duration,
                "channels": target_channels,
                "estimated_bitrate": platform_specs.audio_requirements["bitrate"],
                "file_size_reduction": (
                    len(open(original_file, 'rb').read()) - final_file_size
                ) / len(open(original_file, 'rb').read()) * 100
            }
            
            # Cleanup temporary files
            import os
            os.remove(original_file)
            os.remove(output_file)
            
            return AdaptationResult(
                adapted_url=adapted_url,
                original_url=content.file_url,
                platform=platform,
                format_changes=format_changes,
                quality_metrics=quality_metrics,
                file_size=final_file_size,
                duration=duration,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Audio adaptation failed: {e}")
            return AdaptationResult(
                adapted_url="",
                original_url=content.file_url,
                platform=platform,
                format_changes=[],
                quality_metrics={},
                file_size=0,
                duration=None,
                success=False,
                error_message=str(e)
            )
    
    def _estimate_bitrate(self, file_path: str) -> int:
        """Estimate audio bitrate from file"""
        try:
            import os
            file_size = os.path.getsize(file_path)
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            # Estimate bitrate (in bits per second)
            bitrate = (file_size * 8) / duration
            return int(bitrate)
        except:
            return 128000  # Default bitrate
    
    def _enhance_audio_quality(
        self, 
        audio: np.ndarray, 
        quality: AdaptationQuality
    ) -> np.ndarray:
        """Apply audio quality enhancements"""
        enhanced_audio = audio.copy()
        
        if quality == AdaptationQuality.HIGH:
            # Apply mild noise reduction
            enhanced_audio = self._reduce_noise(enhanced_audio, 0.1)
            
        elif quality == AdaptationQuality.ULTRA:
            # Apply advanced enhancements
            enhanced_audio = self._reduce_noise(enhanced_audio, 0.2)
            enhanced_audio = self._enhance_clarity(enhanced_audio)
            enhanced_audio = self._dynamic_range_compression(enhanced_audio)
        
        return enhanced_audio
    
    def _reduce_noise(self, audio: np.ndarray, strength: float) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        # This is a simplified noise reduction
        # In production, you'd use more sophisticated algorithms
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise floor
        noise_floor = np.percentile(magnitude, 10)
        
        # Apply spectral gating
        mask = magnitude > (noise_floor * (1 + strength))
        cleaned_magnitude = magnitude * mask
        
        # Reconstruct audio
        cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
        cleaned_audio = librosa.istft(cleaned_stft)
        
        return cleaned_audio
    
    def _enhance_clarity(self, audio: np.ndarray) -> np.ndarray:
        """Enhance audio clarity using harmonic enhancement"""
        # Apply harmonic enhancement
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Boost harmonics slightly
        enhanced = harmonic * 1.1 + percussive
        
        return enhanced
    
    def _dynamic_range_compression(self, audio: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compression algorithm
        threshold = 0.7
        ratio = 4.0
        
        compressed = audio.copy()
        mask = np.abs(compressed) > threshold
        
        # Apply compression to samples above threshold
        compressed[mask] = (
            threshold + 
            (np.abs(compressed[mask]) - threshold) / ratio
        ) * np.sign(compressed[mask])
        
        return compressed
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to optimal levels"""
        # Normalize to prevent clipping while maintaining dynamic range
        peak = np.max(np.abs(audio))
        if peak > 0:
            normalized = audio * (0.95 / peak)
        else:
            normalized = audio
        
        return normalized
    
    def _determine_output_format(self, platform: PlatformType) -> str:
        """Determine optimal output format for platform"""
        format_map = {
            PlatformType.SPOTIFY: "mp3",
            PlatformType.YOUTUBE: "mp4",  # Will be used in video container
            PlatformType.INSTAGRAM: "mp4",
            PlatformType.TIKTOK: "mp4",
            PlatformType.TWITTER: "mp4",
            PlatformType.LINKEDIN: "mp4"
        }
        
        return format_map.get(platform, "mp3")


class VideoContentAdapter(BaseContentAdapter):
    """Adapter for video content optimization"""
    
    async def adapt_content(
        self,
        content: ContentModel,
        platform: PlatformType,
        target_format: Optional[ContentFormat] = None,
        quality: AdaptationQuality = AdaptationQuality.HIGH
    ) -> AdaptationResult:
        """Adapt video content for platform requirements"""
        try:
            platform_specs = self.platform_specs[platform]
            
            # Download original video
            original_file = await download_file(content.file_url)
            
            # Load video with moviepy
            video_clip = VideoFileClip(original_file)
            
            # Get current video properties
            current_width, current_height = video_clip.size
            current_duration = video_clip.duration
            current_fps = video_clip.fps
            
            format_changes = []
            adapted_clip = video_clip
            
            # Determine target format if not specified
            if not target_format:
                target_format = self._determine_optimal_format(platform, current_width, current_height)
            
            # Calculate target dimensions
            target_width, target_height = self._calculate_target_dimensions(
                current_width, current_height, target_format, platform_specs
            )
            
            # Resize video if needed
            if (target_width, target_height) != (current_width, current_height):
                adapted_clip = adapted_clip.resize((target_width, target_height))
                format_changes.append(
                    f"Resolution: {current_width}x{current_height} -> {target_width}x{target_height}"
                )
            
            # Adjust duration if needed
            max_duration = platform_specs.max_duration
            if max_duration and current_duration > max_duration:
                adapted_clip = adapted_clip.subclip(0, max_duration)
                format_changes.append(f"Duration trimmed to {max_duration}s")
            
            # Adjust frame rate for platform optimization
            target_fps = self._determine_optimal_fps(platform, current_fps)
            if target_fps != current_fps:
                adapted_clip = adapted_clip.set_fps(target_fps)
                format_changes.append(f"Frame rate: {current_fps}fps -> {target_fps}fps")
            
            # Apply quality enhancements
            if quality in [AdaptationQuality.HIGH, AdaptationQuality.ULTRA]:
                adapted_clip = self._enhance_video_quality(adapted_clip, quality)
                format_changes.append(f"Video enhancement applied ({quality.value})")
            
            # Apply platform-specific optimizations
            adapted_clip = self._apply_platform_optimizations(adapted_clip, platform)
            
            # Audio processing
            if adapted_clip.audio:
                audio_specs = platform_specs.audio_requirements
                if audio_specs:
                    adapted_audio = self._process_video_audio(adapted_clip.audio, audio_specs)
                    adapted_clip = adapted_clip.set_audio(adapted_audio)
                    format_changes.append("Audio optimized for platform")
            
            # Determine output format and codec
            output_format, codec = self._determine_video_output_settings(platform, quality)
            output_file = f"adapted_video_{content.id}_{platform.value}.{output_format}"
            
            # Write video file
            write_params = {
                "filename": output_file,
                "codec": codec,
                "audio_codec": "aac",
                "temp_audiofile": f"temp_audio_{content.id}.m4a",
                "remove_temp": True
            }
            
            # Add quality-specific parameters
            if quality == AdaptationQuality.ULTRA:
                write_params.update({
                    "bitrate": "8000k",
                    "audio_bitrate": "320k"
                })
            elif quality == AdaptationQuality.HIGH:
                write_params.update({
                    "bitrate": "4000k",
                    "audio_bitrate": "192k"
                })
            elif quality == AdaptationQuality.MEDIUM:
                write_params.update({
                    "bitrate": "2000k",
                    "audio_bitrate": "128k"
                })
            else:  # LOW
                write_params.update({
                    "bitrate": "1000k",
                    "audio_bitrate": "96k"
                })
            
            adapted_clip.write_videofile(**write_params)
            
            # Upload adapted file
            adapted_url = await upload_file(output_file)
            
            # Calculate quality metrics
            final_file_size = len(open(output_file, 'rb').read())
            final_duration = adapted_clip.duration
            
            quality_metrics = {
                "resolution": f"{target_width}x{target_height}",
                "duration": final_duration,
                "fps": target_fps,
                "aspect_ratio": self._get_aspect_ratio(target_width, target_height),
                "codec": codec,
                "file_size_reduction": (
                    len(open(original_file, 'rb').read()) - final_file_size
                ) / len(open(original_file, 'rb').read()) * 100 if len(open(original_file, 'rb').read()) > 0 else 0
            }
            
            # Cleanup
            video_clip.close()
            adapted_clip.close()
            import os
            os.remove(original_file)
            os.remove(output_file)
            
            return AdaptationResult(
                adapted_url=adapted_url,
                original_url=content.file_url,
                platform=platform,
                format_changes=format_changes,
                quality_metrics=quality_metrics,
                file_size=final_file_size,
                duration=final_duration,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Video adaptation failed: {e}")
            return AdaptationResult(
                adapted_url="",
                original_url=content.file_url,
                platform=platform,
                format_changes=[],
                quality_metrics={},
                file_size=0,
                duration=None,
                success=False,
                error_message=str(e)
            )
    
    def _determine_optimal_format(
        self, 
        platform: PlatformType, 
        width: int, 
        height: int
    ) -> ContentFormat:
        """Determine optimal content format for platform"""
        aspect_ratio = width / height
        
        platform_preferences = {
            PlatformType.YOUTUBE: ContentFormat.LANDSCAPE,
            PlatformType.INSTAGRAM: ContentFormat.SQUARE if 0.8 <= aspect_ratio <= 1.25 else ContentFormat.PORTRAIT,
            PlatformType.TIKTOK: ContentFormat.PORTRAIT,
            PlatformType.TWITTER: ContentFormat.LANDSCAPE,
            PlatformType.LINKEDIN: ContentFormat.LANDSCAPE
        }
        
        return platform_preferences.get(platform, ContentFormat.LANDSCAPE)
    
    def _determine_optimal_fps(self, platform: PlatformType, current_fps: float) -> float:
        """Determine optimal frame rate for platform"""
        platform_fps = {
            PlatformType.YOUTUBE: 30,
            PlatformType.INSTAGRAM: 30,
            PlatformType.TIKTOK: 30,
            PlatformType.TWITTER: 30,
            PlatformType.LINKEDIN: 30
        }
        
        optimal_fps = platform_fps.get(platform, 30)
        
        # Don't upscale frame rate, only downscale if necessary
        return min(optimal_fps, current_fps)
    
    def _enhance_video_quality(
        self, 
        clip: VideoFileClip, 
        quality: AdaptationQuality
    ) -> VideoFileClip:
        """Apply video quality enhancements"""
        if quality == AdaptationQuality.HIGH:
            # Apply basic enhancements
            enhanced_clip = clip.fx(lambda frame: self._enhance_frame_basic(frame))
            
        elif quality == AdaptationQuality.ULTRA:
            # Apply advanced enhancements
            enhanced_clip = clip.fx(lambda frame: self._enhance_frame_advanced(frame))
        else:
            enhanced_clip = clip
        
        return enhanced_clip
    
    def _enhance_frame_basic(self, frame: np.ndarray) -> np.ndarray:
        """Apply basic frame enhancements"""
        # Convert to PIL Image for processing
        img = Image.fromarray(frame)
        
        # Enhance sharpness slightly
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)
        
        return np.array(img)
    
    def _enhance_frame_advanced(self, frame: np.ndarray) -> np.ndarray:
        """Apply advanced frame enhancements"""
        img = Image.fromarray(frame)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Enhance color saturation
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        
        # Apply unsharp mask for better definition
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        return np.array(img)
    
    def _apply_platform_optimizations(
        self, 
        clip: VideoFileClip, 
        platform: PlatformType
    ) -> VideoFileClip:
        """Apply platform-specific optimizations"""
        optimized_clip = clip
        
        if platform == PlatformType.TIKTOK:
            # TikTok-specific optimizations
            # Add slight zoom effect for mobile viewing
            optimized_clip = optimized_clip.resize(lambda t: 1 + 0.02 * t / clip.duration)
            
        elif platform == PlatformType.INSTAGRAM:
            # Instagram-specific optimizations
            # Ensure square format has proper centering
            if clip.w == clip.h:  # Square format
                optimized_clip = optimized_clip.crop(
                    x_center=clip.w/2, 
                    y_center=clip.h/2, 
                    width=min(clip.w, clip.h), 
                    height=min(clip.w, clip.h)
                )
        
        return optimized_clip
    
    def _process_video_audio(
        self, 
        audio_clip: AudioFileClip, 
        audio_specs: Dict[str, Any]
    ) -> AudioFileClip:
        """Process audio track for video"""
        processed_audio = audio_clip
        
        # Set sample rate
        target_sample_rate = audio_specs.get("sample_rate", 44100)
        processed_audio = processed_audio.set_fps(target_sample_rate)
        
        # Normalize audio levels
        processed_audio = processed_audio.volumex(0.8)  # Slight reduction to prevent clipping
        
        return processed_audio
    
    def _determine_video_output_settings(
        self, 
        platform: PlatformType, 
        quality: AdaptationQuality
    ) -> Tuple[str, str]:
        """Determine output format and codec"""
        # Most platforms prefer MP4 with H.264
        format_settings = {
            PlatformType.YOUTUBE: ("mp4", "libx264"),
            PlatformType.INSTAGRAM: ("mp4", "libx264"),
            PlatformType.TIKTOK: ("mp4", "libx264"),
            PlatformType.TWITTER: ("mp4", "libx264"),
            PlatformType.LINKEDIN: ("mp4", "libx264")
        }
        
        return format_settings.get(platform, ("mp4", "libx264"))


class ImageContentAdapter(BaseContentAdapter):
    """Adapter for image content optimization"""
    
    async def adapt_content(
        self,
        content: ContentModel,
        platform: PlatformType,
        target_format: Optional[ContentFormat] = None,
        quality: AdaptationQuality = AdaptationQuality.HIGH
    ) -> AdaptationResult:
        """Adapt image content for platform requirements"""
        try:
            platform_specs = self.platform_specs[platform]
            
            # Download original image
            original_file = await download_file(content.file_url)
            
            # Load image with PIL
            img = Image.open(original_file)
            current_width, current_height = img.size
            
            format_changes = []
            
            # Determine target format if not specified
            if not target_format:
                target_format = self._determine_optimal_image_format(platform, current_width, current_height)
            
            # Calculate target dimensions
            target_width, target_height = self._calculate_target_dimensions(
                current_width, current_height, target_format, platform_specs
            )
            
            # Resize image if needed
            if (target_width, target_height) != (current_width, current_height):
                # Use high-quality resampling
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                format_changes.append(
                    f"Resolution: {current_width}x{current_height} -> {target_width}x{target_height}"
                )
            
            # Apply quality enhancements
            if quality in [AdaptationQuality.HIGH, AdaptationQuality.ULTRA]:
                img = self._enhance_image_quality(img, quality)
                format_changes.append(f"Image enhancement applied ({quality.value})")
            
            # Apply platform-specific optimizations
            img = self._apply_image_platform_optimizations(img, platform)
            
            # Convert to RGB if necessary (remove alpha channel for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
                format_changes.append("Converted to RGB format")
            
            # Determine output format
            output_format = self._determine_image_output_format(platform)
            output_file = f"adapted_image_{content.id}_{platform.value}.{output_format}"
            
            # Save with quality settings
            save_params = {"format": output_format.upper()}
            
            if output_format.lower() == "jpeg":
                quality_map = {
                    AdaptationQuality.LOW: 70,
                    AdaptationQuality.MEDIUM: 85,
                    AdaptationQuality.HIGH: 95,
                    AdaptationQuality.ULTRA: 98
                }
                save_params["quality"] = quality_map[quality]
                save_params["optimize"] = True
            elif output_format.lower() == "png":
                save_params["optimize"] = True
            
            img.save(output_file, **save_params)
            
            # Upload adapted file
            adapted_url = await upload_file(output_file)
            
            # Calculate quality metrics
            final_file_size = len(open(output_file, 'rb').read())
            
            quality_metrics = {
                "resolution": f"{target_width}x{target_height}",
                "aspect_ratio": self._get_aspect_ratio(target_width, target_height),
                "format": output_format,
                "file_size_reduction": (
                    len(open(original_file, 'rb').read()) - final_file_size
                ) / len(open(original_file, 'rb').read()) * 100 if len(open(original_file, 'rb').read()) > 0 else 0
            }
            
            # Cleanup
            import os
            os.remove(original_file)
            os.remove(output_file)
            
            return AdaptationResult(
                adapted_url=adapted_url,
                original_url=content.file_url,
                platform=platform,
                format_changes=format_changes,
                quality_metrics=quality_metrics,
                file_size=final_file_size,
                duration=None,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Image adaptation failed: {e}")
            return AdaptationResult(
                adapted_url="",
                original_url=content.file_url,
                platform=platform,
                format_changes=[],
                quality_metrics={},
                file_size=0,
                duration=None,
                success=False,
                error_message=str(e)
            )
    
    def _determine_optimal_image_format(
        self, 
        platform: PlatformType, 
        width: int, 
        height: int
    ) -> ContentFormat:
        """Determine optimal image format for platform"""
        aspect_ratio = width / height
        
        if platform == PlatformType.INSTAGRAM:
            if 0.8 <= aspect_ratio <= 1.25:
                return ContentFormat.SQUARE
            elif aspect_ratio < 0.8:
                return ContentFormat.PORTRAIT
            else:
                return ContentFormat.FEED
        elif platform == PlatformType.TWITTER:
            return ContentFormat.LANDSCAPE
        elif platform == PlatformType.LINKEDIN:
            return ContentFormat.LANDSCAPE
        else:
            return ContentFormat.LANDSCAPE  # Default
    
    def _enhance_image_quality(
        self, 
        img: Image.Image, 
        quality: AdaptationQuality
    ) -> Image.Image:
        """Apply image quality enhancements"""
        enhanced_img = img.copy()
        
        if quality == AdaptationQuality.HIGH:
            # Apply basic enhancements
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(enhanced_img)
            enhanced_img = enhancer.enhance(1.1)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = enhancer.enhance(1.05)
            
        elif quality == AdaptationQuality.ULTRA:
            # Apply advanced enhancements
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(enhanced_img)
            enhanced_img = enhancer.enhance(1.2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = enhancer.enhance(1.1)
            
            # Enhance color saturation
            enhancer = ImageEnhance.Color(enhanced_img)
            enhanced_img = enhancer.enhance(1.1)
            
            # Apply unsharp mask
            enhanced_img = enhanced_img.filter(
                ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3)
            )
        
        return enhanced_img
    
    def _apply_image_platform_optimizations(
        self, 
        img: Image.Image, 
        platform: PlatformType
    ) -> Image.Image:
        """Apply platform-specific image optimizations"""
        optimized_img = img
        
        if platform == PlatformType.INSTAGRAM:
            # Instagram prefers slightly saturated images
            enhancer = ImageEnhance.Color(optimized_img)
            optimized_img = enhancer.enhance(1.05)
            
        elif platform == PlatformType.LINKEDIN:
            # LinkedIn prefers professional, clean images
            # Slight reduction in saturation for professional look
            enhancer = ImageEnhance.Color(optimized_img)
            optimized_img = enhancer.enhance(0.95)
        
        return optimized_img
    
    def _determine_image_output_format(self, platform: PlatformType) -> str:
        """Determine optimal output format for platform"""
        # Most platforms prefer JPEG for photos, PNG for graphics with transparency
        return "jpeg"  # Default to JPEG for better compression


class TextContentAdapter(BaseContentAdapter):
    """Adapter for text content optimization"""
    
    async def adapt_content(
        self,
        content: ContentModel,
        platform: PlatformType,
        target_format: Optional[ContentFormat] = None,
        quality: AdaptationQuality = AdaptationQuality.HIGH
    ) -> AdaptationResult:
        """Adapt text content for platform requirements"""
        try:
            platform_specs = self.platform_specs[platform]
            
            # Get original text content
            original_text = content.description or content.title or ""
            
            format_changes = []
            adapted_text = original_text
            
            # Apply platform-specific text optimizations
            adapted_text = self._optimize_text_for_platform(adapted_text, platform)
            
            if adapted_text != original_text:
                format_changes.append("Text optimized for platform")
            
            # Apply hashtag optimization
            hashtags = content.hashtags or []
            optimized_hashtags = self._optimize_hashtags_for_platform(hashtags, platform)
            
            if optimized_hashtags != hashtags:
                format_changes.append("Hashtags optimized for platform")
            
            # Create adapted content (this would typically generate an image or formatted text)
            adapted_content = {
                "text": adapted_text,
                "hashtags": optimized_hashtags,
                "formatted": self._format_text_for_platform(adapted_text, optimized_hashtags, platform)
            }
            
            # For text content, we might generate an image or just return formatted text
            # This is a simplified implementation
            adapted_url = content.file_url  # In reality, you'd create a new formatted version
            
            quality_metrics = {
                "text_length": len(adapted_text),
                "hashtag_count": len(optimized_hashtags),
                "platform_compliance": "optimized"
            }
            
            return AdaptationResult(
                adapted_url=adapted_url,
                original_url=content.file_url,
                platform=platform,
                format_changes=format_changes,
                quality_metrics=quality_metrics,
                file_size=len(adapted_text.encode('utf-8')),
                duration=None,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Text adaptation failed: {e}")
            return AdaptationResult(
                adapted_url="",
                original_url=content.file_url,
                platform=platform,
                format_changes=[],
                quality_metrics={},
                file_size=0,
                duration=None,
                success=False,
                error_message=str(e)
            )
    
    def _optimize_text_for_platform(self, text: str, platform: PlatformType) -> str:
        """Optimize text content for specific platform"""
        # Platform-specific text limits and optimizations
        limits = {
            PlatformType.TWITTER: 280,
            PlatformType.INSTAGRAM: 2200,
            PlatformType.LINKEDIN: 3000,
            PlatformType.TIKTOK: 150,
            PlatformType.YOUTUBE: 5000
        }
        
        max_length = limits.get(platform, 1000)
        
        if len(text) > max_length:
            # Truncate intelligently at sentence boundaries
            truncated = text[:max_length]
            last_sentence = truncated.rfind('. ')
            if last_sentence > max_length * 0.7:
                text = truncated[:last_sentence + 1]
            else:
                text = truncated + "..."
        
        return text
    
    def _optimize_hashtags_for_platform(
        self, 
        hashtags: List[str], 
        platform: PlatformType
    ) -> List[str]:
        """Optimize hashtags for specific platform"""
        limits = {
            PlatformType.TWITTER: 10,
            PlatformType.INSTAGRAM: 30,
            PlatformType.LINKEDIN: 15,
            PlatformType.TIKTOK: 20,
            PlatformType.YOUTUBE: 30
        }
        
        max_hashtags = limits.get(platform, 20)
        
        # Return only the most relevant hashtags
        return hashtags[:max_hashtags]
    
    def _format_text_for_platform(
        self, 
        text: str, 
        hashtags: List[str], 
        platform: PlatformType
    ) -> str:
        """Format text with hashtags for specific platform"""
        formatted_text = text
        
        if hashtags:
            hashtag_text = " ".join([f"#{tag.lstrip('#')}" for tag in hashtags])
            
            if platform == PlatformType.TWITTER:
                # Twitter: add hashtags inline or at end
                formatted_text += f"\n\n{hashtag_text}"
            elif platform == PlatformType.INSTAGRAM:
                # Instagram: separate hashtags block
                formatted_text += f"\n\n{hashtag_text}"
            elif platform == PlatformType.LINKEDIN:
                # LinkedIn: minimal hashtags at end
                formatted_text += f"\n\n{hashtag_text}"
            else:
                formatted_text += f"\n\n{hashtag_text}"
        
        return formatted_text
