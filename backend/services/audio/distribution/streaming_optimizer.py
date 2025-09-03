"""🚀 Streaming Optimizer - Advanced Audio Streaming Optimization

Sophisticated streaming optimization system for adaptive bitrate streaming,
platform-specific optimization, and real-time content delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class StreamingPlatform(Enum):
    """Supported streaming platforms"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    TIDAL = "tidal"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    GENERIC = "generic"


class AudioQuality(Enum):
    """Audio quality levels for streaming"""
    LOW = "low"          # 64-96 kbps
    MEDIUM = "medium"    # 128-192 kbps
    HIGH = "high"        # 256-320 kbps
    LOSSLESS = "lossless" # FLAC/ALAC
    HI_RES = "hi_res"    # 24-bit/96kHz+


class StreamingFormat(Enum):
    """Streaming audio formats"""
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    FLAC = "flac"
    OPUS = "opus"
    M4A = "m4a"


@dataclass
class StreamingSettings:
    """Streaming optimization configuration"""
    platform: StreamingPlatform = StreamingPlatform.GENERIC
    target_quality: AudioQuality = AudioQuality.HIGH
    format: StreamingFormat = StreamingFormat.AAC
    adaptive_bitrate: bool = True
    loudness_normalization: bool = True
    target_lufs: float = -14.0
    gapless_playback: bool = True
    metadata_optimization: bool = True


@dataclass
class OptimizedStream:
    """Optimized audio stream data"""
    audio_data: np.ndarray
    format: StreamingFormat
    bitrate: int
    sample_rate: int
    channels: int
    metadata: Dict[str, Any]
    platform_optimizations: List[str]


@dataclass
class StreamingOptimizationResult:
    """Streaming optimization result"""
    optimized_streams: Dict[AudioQuality, OptimizedStream]
    original_size_mb: float
    total_optimized_size_mb: float
    compression_ratio: float
    processing_time: float
    settings_used: StreamingSettings
    metadata: Dict[str, Any]


class StreamingOptimizer:
    """
    Advanced audio streaming optimization system.
    
    Provides platform-specific optimization, adaptive bitrate streaming,
    and comprehensive audio preparation for various streaming services.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the streaming optimizer.
        
        Args:
            config: Configuration dictionary for optimization parameters
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 44100)
        
        # Platform-specific configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Quality level configurations
        self.quality_configs = self._initialize_quality_configs()
        
        logger.info("StreamingOptimizer initialized successfully")
    
    def _initialize_platform_configs(self) -> Dict[StreamingPlatform, Dict[str, Any]]:
        """Initialize platform-specific optimization configurations"""
        return {
            StreamingPlatform.SPOTIFY: {
                'preferred_format': StreamingFormat.OGG,
                'loudness_target': -14.0,
                'quality_tiers': [AudioQuality.LOW, AudioQuality.MEDIUM, AudioQuality.HIGH],
                'gapless_support': True,
                'metadata_fields': ['title', 'artist', 'album', 'track_number', 'isrc']
            },
            StreamingPlatform.APPLE_MUSIC: {
                'preferred_format': StreamingFormat.AAC,
                'loudness_target': -16.0,
                'quality_tiers': [AudioQuality.MEDIUM, AudioQuality.HIGH, AudioQuality.LOSSLESS],
                'gapless_support': True,
                'metadata_fields': ['title', 'artist', 'album', 'genre', 'artwork']
            },
            StreamingPlatform.YOUTUBE_MUSIC: {
                'preferred_format': StreamingFormat.AAC,
                'loudness_target': -14.0,
                'quality_tiers': [AudioQuality.LOW, AudioQuality.MEDIUM, AudioQuality.HIGH],
                'gapless_support': False,
                'metadata_fields': ['title', 'artist', 'description', 'tags']
            },
            StreamingPlatform.AMAZON_MUSIC: {
                'preferred_format': StreamingFormat.FLAC,
                'loudness_target': -14.0,
                'quality_tiers': [AudioQuality.MEDIUM, AudioQuality.HIGH, AudioQuality.LOSSLESS, AudioQuality.HI_RES],
                'gapless_support': True,
                'metadata_fields': ['title', 'artist', 'album', 'genre', 'asin']
            },
            StreamingPlatform.TIDAL: {
                'preferred_format': StreamingFormat.FLAC,
                'loudness_target': -14.0,
                'quality_tiers': [AudioQuality.HIGH, AudioQuality.LOSSLESS, AudioQuality.HI_RES],
                'gapless_support': True,
                'metadata_fields': ['title', 'artist', 'album', 'composer', 'mqa_info']
            },
            StreamingPlatform.SOUNDCLOUD: {
                'preferred_format': StreamingFormat.MP3,
                'loudness_target': -16.0,
                'quality_tiers': [AudioQuality.MEDIUM, AudioQuality.HIGH],
                'gapless_support': False,
                'metadata_fields': ['title', 'artist', 'description', 'genre', 'tags']
            }
        }
    
    def _initialize_quality_configs(self) -> Dict[AudioQuality, Dict[str, Any]]:
        """Initialize quality level configurations"""
        return {
            AudioQuality.LOW: {
                'bitrate_range': (64, 96),
                'sample_rate': 22050,
                'channels': 1,  # Mono for lowest quality
                'compression_level': 'high'
            },
            AudioQuality.MEDIUM: {
                'bitrate_range': (128, 192),
                'sample_rate': 44100,
                'channels': 2,
                'compression_level': 'medium'
            },
            AudioQuality.HIGH: {
                'bitrate_range': (256, 320),
                'sample_rate': 44100,
                'channels': 2,
                'compression_level': 'low'
            },
            AudioQuality.LOSSLESS: {
                'bitrate_range': (700, 1411),  # FLAC typical range
                'sample_rate': 44100,
                'channels': 2,
                'compression_level': 'lossless'
            },
            AudioQuality.HI_RES: {
                'bitrate_range': (2000, 9216),  # 24-bit/96kHz+
                'sample_rate': 96000,
                'channels': 2,
                'compression_level': 'lossless'
            }
        }
    
    async def optimize_for_streaming(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        settings: Optional[StreamingSettings] = None,
        quality_levels: Optional[List[AudioQuality]] = None
    ) -> StreamingOptimizationResult:
        """
        Optimize audio for streaming across multiple quality levels.
        
        Args:
            audio_data: Original audio data
            settings: Streaming optimization settings
            quality_levels: List of quality levels to generate
            
        Returns:
            StreamingOptimizationResult: Optimized streams and metadata
        """
        start_time = time.time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            settings = settings or StreamingSettings()
            
            # Determine quality levels to generate
            if quality_levels is None:
                platform_config = self.platform_configs.get(settings.platform, {})
                quality_levels = platform_config.get('quality_tiers', [AudioQuality.MEDIUM, AudioQuality.HIGH])
            
            # Calculate original size
            original_size_mb = len(audio_array) * 4 / (1024 * 1024)  # 32-bit float
            
            # Generate optimized streams for each quality level
            optimized_streams = {}
            total_optimized_size = 0.0
            
            for quality in quality_levels:
                optimized_stream = await self._create_optimized_stream(
                    audio_array, sr, quality, settings
                )
                optimized_streams[quality] = optimized_stream
                
                # Estimate compressed size (simplified)
                quality_config = self.quality_configs[quality]
                estimated_bitrate = np.mean(quality_config['bitrate_range'])
                duration_seconds = len(audio_array) / sr
                estimated_size_mb = (estimated_bitrate * duration_seconds) / (8 * 1024)  # Convert to MB
                total_optimized_size += estimated_size_mb
            
            # Calculate compression ratio
            compression_ratio = original_size_mb / max(total_optimized_size, 0.001)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return StreamingOptimizationResult(
                optimized_streams=optimized_streams,
                original_size_mb=original_size_mb,
                total_optimized_size_mb=total_optimized_size,
                compression_ratio=compression_ratio,
                processing_time=processing_time,
                settings_used=settings,
                metadata={
                    'platform': settings.platform.value,
                    'quality_levels_generated': len(quality_levels),
                    'original_duration': len(audio_array) / sr,
                    'original_sample_rate': sr
                }
            )
            
        except Exception as e:
            logger.error(f"Streaming optimization failed: {e}")
            processing_time = time.time() - start_time
            
            return StreamingOptimizationResult(
                optimized_streams={},
                original_size_mb=0.0,
                total_optimized_size_mb=0.0,
                compression_ratio=1.0,
                processing_time=processing_time,
                settings_used=settings or StreamingSettings(),
                metadata={'error': str(e)}
            )
    
    async def optimize_for_platform(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        platform: StreamingPlatform,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StreamingOptimizationResult:
        """
        Optimize audio specifically for a target streaming platform.
        
        Args:
            audio_data: Original audio data
            platform: Target streaming platform
            metadata: Audio metadata
            
        Returns:
            StreamingOptimizationResult: Platform-optimized streams
        """
        try:
            # Get platform-specific configuration
            platform_config = self.platform_configs.get(platform, {})
            
            # Create platform-specific settings
            settings = StreamingSettings(
                platform=platform,
                format=platform_config.get('preferred_format', StreamingFormat.AAC),
                target_lufs=platform_config.get('loudness_target', -14.0),
                gapless_playback=platform_config.get('gapless_support', True),
                metadata_optimization=True
            )
            
            # Get platform quality tiers
            quality_levels = platform_config.get('quality_tiers', [AudioQuality.MEDIUM, AudioQuality.HIGH])
            
            # Optimize for platform
            result = await self.optimize_for_streaming(audio_data, settings, quality_levels)
            
            # Add platform-specific metadata
            if metadata:
                platform_metadata = await self._optimize_metadata_for_platform(metadata, platform)
                for stream in result.optimized_streams.values():
                    stream.metadata.update(platform_metadata)
            
            return result
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            # Return basic optimization
            return await self.optimize_for_streaming(audio_data)
    
    def _load_audio(self, audio_data: Union[np.ndarray, bytes, str, Path]) -> Tuple[np.ndarray, int]:
        """Load audio data into numpy array"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.sample_rate
        elif isinstance(audio_data, (str, Path)):
            audio_array, sr = librosa.load(str(audio_data), sr=self.sample_rate, mono=False)
            return audio_array, sr
        elif isinstance(audio_data, bytes):
            # Convert bytes to numpy array (simplified)
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            return audio_array, self.sample_rate
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
    
    async def _create_optimized_stream(
        self,
        audio: np.ndarray,
        sr: int,
        quality: AudioQuality,
        settings: StreamingSettings
    ) -> OptimizedStream:
        """Create optimized stream for specific quality level"""
        try:
            quality_config = self.quality_configs[quality]
            platform_config = self.platform_configs.get(settings.platform, {})
            
            # Resample if necessary
            target_sr = quality_config['sample_rate']
            if sr != target_sr:
                if audio.ndim == 1:
                    resampled_audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                else:
                    resampled_audio = np.array([
                        librosa.resample(audio[0], orig_sr=sr, target_sr=target_sr),
                        librosa.resample(audio[1], orig_sr=sr, target_sr=target_sr)
                    ])
            else:
                resampled_audio = audio
            
            # Convert to target channels
            target_channels = quality_config['channels']
            if audio.ndim == 2 and target_channels == 1:
                # Stereo to mono
                optimized_audio = np.mean(resampled_audio, axis=0)
            elif audio.ndim == 1 and target_channels == 2:
                # Mono to stereo
                optimized_audio = np.array([resampled_audio, resampled_audio])
            else:
                optimized_audio = resampled_audio
            
            # Apply loudness normalization if enabled
            if settings.loudness_normalization:
                optimized_audio = await self._normalize_loudness(
                    optimized_audio, target_sr, settings.target_lufs
                )
            
            # Apply platform-specific optimizations
            platform_optimizations = []
            
            if settings.gapless_playback and platform_config.get('gapless_support', False):
                optimized_audio = await self._optimize_for_gapless(optimized_audio, target_sr)
                platform_optimizations.append("gapless_playback")
            
            # Dynamic range optimization based on platform
            if settings.platform in [StreamingPlatform.SPOTIFY, StreamingPlatform.YOUTUBE_MUSIC]:
                optimized_audio = await self._optimize_dynamic_range(optimized_audio, target_sr)
                platform_optimizations.append("dynamic_range_optimization")
            
            # Calculate target bitrate
            bitrate_range = quality_config['bitrate_range']
            target_bitrate = int(np.mean(bitrate_range))
            
            # Create optimized stream
            stream = OptimizedStream(
                audio_data=optimized_audio,
                format=settings.format,
                bitrate=target_bitrate,
                sample_rate=target_sr,
                channels=target_channels,
                metadata={
                    'quality': quality.value,
                    'platform': settings.platform.value,
                    'loudness_lufs': settings.target_lufs if settings.loudness_normalization else None
                },
                platform_optimizations=platform_optimizations
            )
            
            return stream
            
        except Exception as e:
            logger.warning(f"Stream optimization failed for quality {quality}: {e}")
            # Return minimal stream
            return OptimizedStream(
                audio_data=audio,
                format=settings.format,
                bitrate=128,
                sample_rate=sr,
                channels=1 if audio.ndim == 1 else 2,
                metadata={'error': str(e)},
                platform_optimizations=[]
            )
    
    async def _normalize_loudness(
        self,
        audio: np.ndarray,
        sr: int,
        target_lufs: float
    ) -> np.ndarray:
        """Normalize audio loudness to target LUFS"""
        try:
            # Calculate current LUFS (simplified implementation)
            if audio.ndim == 1:
                rms = np.sqrt(np.mean(audio ** 2))
            else:
                # Stereo RMS
                left_rms = np.sqrt(np.mean(audio[0] ** 2))
                right_rms = np.sqrt(np.mean(audio[1] ** 2))
                rms = np.sqrt((left_rms ** 2 + right_rms ** 2) / 2)
            
            if rms > 0:
                # Simplified LUFS calculation
                current_lufs = -0.691 + 10 * np.log10(rms ** 2)
                
                # Calculate required gain
                gain_db = target_lufs - current_lufs
                gain_linear = 10 ** (gain_db / 20)
                
                # Apply gain with limiting
                normalized_audio = audio * gain_linear
                
                # Soft limiting to prevent clipping
                peak = np.max(np.abs(normalized_audio))
                if peak > 0.95:
                    normalized_audio = normalized_audio * (0.95 / peak)
                
                return normalized_audio
            
            return audio
            
        except Exception as e:
            logger.warning(f"Loudness normalization failed: {e}")
            return audio
    
    async def _optimize_for_gapless(
        self,
        audio: np.ndarray,
        sr: int
    ) -> np.ndarray:
        """Optimize audio for gapless playback"""
        try:
            # Remove silence from beginning and end
            silence_threshold = 0.01
            
            if audio.ndim == 1:
                # Mono
                non_silent = np.abs(audio) > silence_threshold
                if np.any(non_silent):
                    start_idx = np.argmax(non_silent)
                    end_idx = len(audio) - np.argmax(non_silent[::-1])
                    trimmed_audio = audio[start_idx:end_idx]
                else:
                    trimmed_audio = audio
            else:
                # Stereo
                non_silent = (np.abs(audio[0]) > silence_threshold) | (np.abs(audio[1]) > silence_threshold)
                if np.any(non_silent):
                    start_idx = np.argmax(non_silent)
                    end_idx = len(audio[0]) - np.argmax(non_silent[::-1])
                    trimmed_audio = audio[:, start_idx:end_idx]
                else:
                    trimmed_audio = audio
            
            # Apply gentle fade in/out for smooth transitions
            fade_samples = min(int(0.01 * sr), len(trimmed_audio[0]) // 10 if audio.ndim == 2 else len(trimmed_audio) // 10)
            
            if fade_samples > 0:
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                
                if trimmed_audio.ndim == 1:
                    trimmed_audio[:fade_samples] *= fade_in
                    trimmed_audio[-fade_samples:] *= fade_out
                else:
                    trimmed_audio[:, :fade_samples] *= fade_in
                    trimmed_audio[:, -fade_samples:] *= fade_out
            
            return trimmed_audio
            
        except Exception as e:
            logger.warning(f"Gapless optimization failed: {e}")
            return audio
    
    async def _optimize_dynamic_range(
        self,
        audio: np.ndarray,
        sr: int
    ) -> np.ndarray:
        """Optimize dynamic range for streaming platforms"""
        try:
            # Apply gentle compression for streaming platforms
            # This ensures consistent playback across different devices
            
            if audio.ndim == 1:
                optimized = await self._apply_gentle_compression(audio, sr)
            else:
                # Process each channel
                left_optimized = await self._apply_gentle_compression(audio[0], sr)
                right_optimized = await self._apply_gentle_compression(audio[1], sr)
                optimized = np.array([left_optimized, right_optimized])
            
            return optimized
            
        except Exception as e:
            logger.warning(f"Dynamic range optimization failed: {e}")
            return audio
    
    async def _apply_gentle_compression(
        self,
        audio: np.ndarray,
        sr: int
    ) -> np.ndarray:
        """Apply gentle compression for streaming optimization"""
        try:
            # Simple compression algorithm
            threshold = 0.7
            ratio = 2.0
            attack_time = 0.01  # 10ms
            release_time = 0.1  # 100ms
            
            # Calculate envelope
            envelope = np.abs(audio)
            
            # Smooth envelope
            attack_samples = int(attack_time * sr)
            release_samples = int(release_time * sr)
            
            gain_reduction = np.ones_like(envelope)
            
            for i in range(1, len(envelope)):
                if envelope[i] > threshold:
                    # Calculate required gain reduction
                    overshoot = envelope[i] / threshold
                    target_gain = 1.0 / (1.0 + (overshoot - 1.0) * (ratio - 1.0) / ratio)
                    
                    # Apply attack/release smoothing
                    if gain_reduction[i-1] > target_gain:
                        # Attack
                        gain_reduction[i] = target_gain + (gain_reduction[i-1] - target_gain) * np.exp(-1.0 / attack_samples)
                    else:
                        # Release
                        gain_reduction[i] = target_gain + (gain_reduction[i-1] - target_gain) * np.exp(-1.0 / release_samples)
                else:
                    # Release towards 1.0
                    gain_reduction[i] = 1.0 + (gain_reduction[i-1] - 1.0) * np.exp(-1.0 / release_samples)
            
            compressed = audio * gain_reduction
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Gentle compression failed: {e}")
            return audio
    
    async def _optimize_metadata_for_platform(
        self,
        metadata: Dict[str, Any],
        platform: StreamingPlatform
    ) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        try:
            platform_config = self.platform_configs.get(platform, {})
            required_fields = platform_config.get('metadata_fields', [])
            
            optimized_metadata = {}
            
            # Map common metadata fields
            field_mappings = {
                'title': ['title', 'track_title', 'song_title'],
                'artist': ['artist', 'performer', 'creator'],
                'album': ['album', 'album_title'],
                'genre': ['genre', 'style', 'category'],
                'track_number': ['track_number', 'track', 'position']
            }
            
            for required_field in required_fields:
                if required_field in field_mappings:
                    for possible_key in field_mappings[required_field]:
                        if possible_key in metadata:
                            optimized_metadata[required_field] = metadata[possible_key]
                            break
                elif required_field in metadata:
                    optimized_metadata[required_field] = metadata[required_field]
            
            # Platform-specific optimizations
            if platform == StreamingPlatform.SPOTIFY:
                # Spotify-specific metadata optimizations
                if 'isrc' not in optimized_metadata and 'isrc_code' in metadata:
                    optimized_metadata['isrc'] = metadata['isrc_code']
            
            elif platform == StreamingPlatform.YOUTUBE_MUSIC:
                # YouTube Music optimizations
                if 'description' not in optimized_metadata:
                    # Create description from available metadata
                    desc_parts = []
                    if 'artist' in optimized_metadata:
                        desc_parts.append(f"Artist: {optimized_metadata['artist']}")
                    if 'album' in optimized_metadata:
                        desc_parts.append(f"Album: {optimized_metadata['album']}")
                    if desc_parts:
                        optimized_metadata['description'] = ' | '.join(desc_parts)
            
            elif platform == StreamingPlatform.APPLE_MUSIC:
                # Apple Music optimizations
                if 'artwork' not in optimized_metadata and 'cover_art' in metadata:
                    optimized_metadata['artwork'] = metadata['cover_art']
            
            return optimized_metadata
            
        except Exception as e:
            logger.warning(f"Metadata optimization failed: {e}")
            return metadata
    
    async def analyze_streaming_compatibility(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        target_platforms: Optional[List[StreamingPlatform]] = None
    ) -> Dict[StreamingPlatform, Dict[str, Any]]:
        """
        Analyze audio compatibility with streaming platforms.
        
        Args:
            audio_data: Audio to analyze
            target_platforms: Platforms to analyze (all if None)
            
        Returns:
            Dict with compatibility analysis for each platform
        """
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            
            if target_platforms is None:
                target_platforms = list(StreamingPlatform)
            
            compatibility_report = {}
            
            for platform in target_platforms:
                platform_config = self.platform_configs.get(platform, {})
                
                analysis = {
                    'compatible': True,
                    'recommendations': [],
                    'optimal_settings': {},
                    'quality_tiers_supported': platform_config.get('quality_tiers', []),
                    'preferred_format': platform_config.get('preferred_format', StreamingFormat.AAC).value
                }
                
                # Analyze loudness
                current_lufs = await self._calculate_lufs(audio_array, sr)
                target_lufs = platform_config.get('loudness_target', -14.0)
                
                if abs(current_lufs - target_lufs) > 2.0:
                    analysis['recommendations'].append(
                        f"Adjust loudness from {current_lufs:.1f} LUFS to {target_lufs:.1f} LUFS"
                    )
                
                # Analyze sample rate
                if sr not in [44100, 48000, 96000]:
                    analysis['recommendations'].append(
                        f"Consider resampling from {sr} Hz to 44100 Hz for better compatibility"
                    )
                
                # Analyze dynamic range
                dynamic_range = await self._calculate_dynamic_range(audio_array, sr)
                if dynamic_range < 6.0:
                    analysis['recommendations'].append(
                        "Audio appears heavily compressed - consider using less compression for better quality"
                    )
                elif dynamic_range > 20.0:
                    analysis['recommendations'].append(
                        "High dynamic range detected - may benefit from gentle compression for streaming"
                    )
                
                # Platform-specific analysis
                if platform == StreamingPlatform.SPOTIFY:
                    if dynamic_range < 8.0:
                        analysis['recommendations'].append(
                            "Spotify prefers moderate dynamic range (8-12 DR) for optimal playback"
                        )
                
                elif platform == StreamingPlatform.TIDAL:
                    if sr < 44100:
                        analysis['compatible'] = False
                        analysis['recommendations'].append(
                            "TIDAL requires minimum 44.1kHz sample rate for high-quality streaming"
                        )
                
                # Set optimal settings
                analysis['optimal_settings'] = {
                    'loudness_target': target_lufs,
                    'format': platform_config.get('preferred_format', StreamingFormat.AAC).value,
                    'gapless_support': platform_config.get('gapless_support', False)
                }
                
                compatibility_report[platform] = analysis
            
            return compatibility_report
            
        except Exception as e:
            logger.error(f"Streaming compatibility analysis failed: {e}")
            return {}
    
    async def _calculate_lufs(self, audio: np.ndarray, sr: int) -> float:
        """Calculate integrated loudness in LUFS"""
        try:
            # Simplified LUFS calculation
            if audio.ndim == 1:
                rms = np.sqrt(np.mean(audio ** 2))
            else:
                left_rms = np.sqrt(np.mean(audio[0] ** 2))
                right_rms = np.sqrt(np.mean(audio[1] ** 2))
                rms = np.sqrt((left_rms ** 2 + right_rms ** 2) / 2)
            
            if rms > 0:
                lufs = -0.691 + 10 * np.log10(rms ** 2)
                return float(lufs)
            else:
                return -80.0
                
        except Exception as e:
            logger.warning(f"LUFS calculation failed: {e}")
            return -23.0
    
    async def _calculate_dynamic_range(self, audio: np.ndarray, sr: int) -> float:
        """Calculate dynamic range"""
        try:
            # Calculate RMS in windows
            window_size = int(0.3 * sr)  # 300ms windows
            hop_size = window_size // 2
            
            rms_values = []
            
            for i in range(0, len(audio) - window_size, hop_size):
                if audio.ndim == 1:
                    window = audio[i:i + window_size]
                    rms = np.sqrt(np.mean(window ** 2))
                else:
                    window_left = audio[0, i:i + window_size]
                    window_right = audio[1, i:i + window_size]
                    rms = np.sqrt((np.mean(window_left ** 2) + np.mean(window_right ** 2)) / 2)
                
                if rms > 0:
                    rms_values.append(rms)
            
            if len(rms_values) >= 2:
                high_percentile = np.percentile(rms_values, 95)
                low_percentile = np.percentile(rms_values, 10)
                
                if low_percentile > 0:
                    dr = 20 * np.log10(high_percentile / low_percentile)
                    return float(dr)
            
            return 6.0  # Default DR value
            
        except Exception as e:
            logger.warning(f"Dynamic range calculation failed: {e}")
            return 6.0