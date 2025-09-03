"""📡 Streaming Optimizer - Advanced Audio Streaming Optimization

Professional streaming optimization for various platforms and network conditions.
Adaptive bitrate, format optimization, and delivery optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid
import tempfile
import os
import time

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    import torch
    import torchaudio
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

try:
    # Import existing audio processing components
    from ....ai_engine.audio_processing.formats import FormatConverter
    from ....ai_engine.audio_processing.core import AudioProcessor
    EXISTING_STREAMING_AVAILABLE = True
except ImportError:
    EXISTING_STREAMING_AVAILABLE = False

logger = logging.getLogger(__name__)


class StreamingPlatform(Enum):
    """Streaming platform targets"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"
    TIDAL = "tidal"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    DISCORD = "discord"
    CUSTOM = "custom"


class NetworkCondition(Enum):
    """Network condition types"""
    EXCELLENT = "excellent"  # >10 Mbps
    GOOD = "good"           # 2-10 Mbps
    MODERATE = "moderate"   # 512 Kbps - 2 Mbps
    POOR = "poor"          # 128-512 Kbps
    VERY_POOR = "very_poor" # <128 Kbps


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    QUALITY_PRIORITY = "quality_priority"
    BANDWIDTH_PRIORITY = "bandwidth_priority"
    BALANCED = "balanced"
    REAL_TIME = "real_time"
    STORAGE_EFFICIENT = "storage_efficient"


class AudioCodec(Enum):
    """Audio codecs for streaming"""
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    FLAC = "flac"
    WAV = "wav"
    M4A = "m4a"


@dataclass
class StreamingSettings:
    """Streaming optimization settings"""
    target_platform: StreamingPlatform
    network_condition: NetworkCondition
    optimization_strategy: OptimizationStrategy
    target_bitrates: List[int] = None  # Kbps
    target_formats: List[AudioCodec] = None
    enable_adaptive_bitrate: bool = True
    enable_psychoacoustic_optimization: bool = True
    max_file_size_mb: Optional[float] = None
    target_latency_ms: Optional[float] = None
    custom_parameters: Optional[Dict[str, Any]] = None


@dataclass
class StreamingProfile:
    """Streaming profile for specific platform"""
    platform: StreamingPlatform
    recommended_formats: List[AudioCodec]
    bitrate_tiers: List[int]  # Kbps
    sample_rates: List[int]   # Hz
    max_file_size_mb: Optional[float]
    loudness_target_lufs: float
    dynamic_range_target: Optional[float]
    special_requirements: Dict[str, Any]


@dataclass
class OptimizationResult:
    """Streaming optimization result"""
    success: bool
    optimized_variants: List[Dict[str, Any]]
    original_size_mb: float
    total_optimized_size_mb: float
    size_reduction_percent: float
    processing_time: float
    quality_scores: Dict[str, float]
    bandwidth_savings: Dict[str, float]
    compatibility_report: Dict[str, Any]
    recommendations: List[str]
    error_message: Optional[str] = None


@dataclass
class AdaptiveBitrateResult:
    """Adaptive bitrate streaming result"""
    variants: List[Dict[str, Any]]
    manifest_data: Dict[str, Any]
    segment_duration: float
    total_segments: int
    bandwidth_ladder: List[int]
    switching_points: List[Dict[str, Any]]


class StreamingOptimizer:
    """Advanced audio streaming optimization engine"""
    
    def __init__(self,
                 enable_adaptive_streaming: bool = True,
                 default_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
                 cache_optimizations: bool = True):
        """
        Initialize streaming optimizer
        
        Args:
            enable_adaptive_streaming: Enable adaptive bitrate streaming
            default_strategy: Default optimization strategy
            cache_optimizations: Cache optimization results
        """
        self.enable_adaptive_streaming = enable_adaptive_streaming
        self.default_strategy = default_strategy
        self.cache_optimizations = cache_optimizations
        
        # Initialize existing audio processing components if available
        self.format_converter = None
        self.audio_processor = None
        
        if EXISTING_STREAMING_AVAILABLE:
            try:
                self.format_converter = FormatConverter()
                self.audio_processor = AudioProcessor()
                logger.info("Existing streaming components initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize existing components: {e}")
        
        # Streaming profiles and optimization cache
        self.streaming_profiles = {}
        self.optimization_cache = {}
        
        # Initialize platform profiles
        self._initialize_platform_profiles()
        
        if STREAMING_AVAILABLE:
            self._load_optimization_models()
        
        logger.info(f"StreamingOptimizer initialized with {default_strategy.value} strategy")
    
    async def optimize_for_streaming(self,
                                   audio_data: Union[bytes, BinaryIO],
                                   settings: StreamingSettings) -> OptimizationResult:
        """
        Optimize audio for streaming platforms
        
        Args:
            audio_data: Audio data to optimize
            settings: Streaming optimization settings
            
        Returns:
            Optimization result with multiple variants
        """
        try:
            start_time = time.time()
            
            # Load audio
            audio_array, sample_rate = await self._load_audio(audio_data)
            original_size = len(await self._convert_to_bytes(audio_array, sample_rate))
            original_size_mb = original_size / (1024 * 1024)
            
            # Get platform profile
            platform_profile = self.streaming_profiles.get(
                settings.target_platform, 
                self._get_default_profile()
            )
            
            # Determine optimization parameters
            optimization_params = await self._calculate_optimization_parameters(
                audio_array, sample_rate, settings, platform_profile
            )
            
            # Pre-process audio for optimization
            preprocessed_audio = await self._preprocess_for_streaming(
                audio_array, sample_rate, settings, platform_profile
            )
            
            # Generate optimized variants
            optimized_variants = []
            total_optimized_size = 0
            
            # Determine target formats and bitrates
            target_formats = settings.target_formats or platform_profile.recommended_formats
            target_bitrates = settings.target_bitrates or platform_profile.bitrate_tiers
            
            for codec in target_formats:
                for bitrate in target_bitrates:
                    try:
                        variant = await self._create_optimized_variant(
                            preprocessed_audio, sample_rate, codec, bitrate,
                            settings, platform_profile, optimization_params
                        )
                        
                        if variant['success']:
                            optimized_variants.append(variant)
                            total_optimized_size += variant['file_size_bytes']
                            
                    except Exception as e:
                        logger.warning(f"Failed to create variant {codec.value}@{bitrate}kbps: {e}")
                        continue
            
            # Calculate metrics
            total_optimized_size_mb = total_optimized_size / (1024 * 1024)
            size_reduction_percent = ((original_size_mb - total_optimized_size_mb) / original_size_mb) * 100
            
            # Assess quality scores
            quality_scores = await self._assess_variant_quality(
                optimized_variants, audio_array, sample_rate
            )
            
            # Calculate bandwidth savings
            bandwidth_savings = await self._calculate_bandwidth_savings(
                optimized_variants, settings.network_condition
            )
            
            # Generate compatibility report
            compatibility_report = await self._generate_compatibility_report(
                optimized_variants, settings.target_platform
            )
            
            # Generate recommendations
            recommendations = await self._generate_streaming_recommendations(
                optimized_variants, settings, platform_profile, quality_scores
            )
            
            processing_time = time.time() - start_time
            
            # Cache results if enabled
            if self.cache_optimizations:
                cache_key = self._generate_cache_key(audio_array, settings)
                self.optimization_cache[cache_key] = {
                    'result': optimized_variants,
                    'timestamp': time.time()
                }
            
            return OptimizationResult(
                success=True,
                optimized_variants=optimized_variants,
                original_size_mb=original_size_mb,
                total_optimized_size_mb=total_optimized_size_mb,
                size_reduction_percent=size_reduction_percent,
                processing_time=processing_time,
                quality_scores=quality_scores,
                bandwidth_savings=bandwidth_savings,
                compatibility_report=compatibility_report,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Streaming optimization failed: {e}")
            return OptimizationResult(
                success=False,
                optimized_variants=[],
                original_size_mb=0.0,
                total_optimized_size_mb=0.0,
                size_reduction_percent=0.0,
                processing_time=0.0,
                quality_scores={},
                bandwidth_savings={},
                compatibility_report={},
                recommendations=[],
                error_message=str(e)
            )
    
    async def create_adaptive_bitrate_stream(self,
                                           audio_data: Union[bytes, BinaryIO],
                                           settings: StreamingSettings,
                                           segment_duration: float = 6.0) -> AdaptiveBitrateResult:
        """
        Create adaptive bitrate streaming variants
        
        Args:
            audio_data: Audio data to process
            settings: Streaming settings
            segment_duration: Duration of each segment in seconds
            
        Returns:
            Adaptive bitrate streaming result
        """
        try:
            # Load audio
            audio_array, sample_rate = await self._load_audio(audio_data)
            
            # Get platform profile
            platform_profile = self.streaming_profiles.get(
                settings.target_platform,
                self._get_default_profile()
            )
            
            # Create bandwidth ladder
            bandwidth_ladder = await self._create_bandwidth_ladder(
                settings.network_condition, platform_profile
            )
            
            # Segment audio
            segments = await self._segment_audio(
                audio_array, sample_rate, segment_duration
            )
            
            # Create variants for each bitrate
            variants = []
            for bitrate in bandwidth_ladder:
                variant_segments = []
                
                for i, segment in enumerate(segments):
                    # Optimize each segment
                    optimized_segment = await self._optimize_segment(
                        segment, sample_rate, bitrate, settings, platform_profile
                    )
                    variant_segments.append(optimized_segment)
                
                variant = {
                    'bitrate_kbps': bitrate,
                    'codec': AudioCodec.AAC.value,  # Default for adaptive streaming
                    'segments': variant_segments,
                    'total_duration': len(audio_array) / sample_rate,
                    'bandwidth_requirement': bitrate * 1000,  # bps
                    'recommended_network': self._get_recommended_network_for_bitrate(bitrate)
                }
                variants.append(variant)
            
            # Create switching points
            switching_points = await self._calculate_switching_points(
                variants, segments, bandwidth_ladder
            )
            
            # Generate manifest
            manifest_data = await self._generate_adaptive_manifest(
                variants, segment_duration, settings.target_platform
            )
            
            return AdaptiveBitrateResult(
                variants=variants,
                manifest_data=manifest_data,
                segment_duration=segment_duration,
                total_segments=len(segments),
                bandwidth_ladder=bandwidth_ladder,
                switching_points=switching_points
            )
            
        except Exception as e:
            logger.error(f"Adaptive bitrate stream creation failed: {e}")
            raise
    
    async def optimize_for_network_condition(self,
                                           audio_data: Union[bytes, BinaryIO],
                                           network_condition: NetworkCondition,
                                           target_platform: StreamingPlatform = StreamingPlatform.CUSTOM) -> Dict[str, Any]:
        """
        Optimize audio for specific network conditions
        
        Args:
            audio_data: Audio data to optimize
            network_condition: Target network condition
            target_platform: Target streaming platform
            
        Returns:
            Network-optimized audio data and metadata
        """
        try:
            # Create settings for network condition
            settings = StreamingSettings(
                target_platform=target_platform,
                network_condition=network_condition,
                optimization_strategy=OptimizationStrategy.BANDWIDTH_PRIORITY,
                enable_adaptive_bitrate=True
            )
            
            # Get optimal parameters for network condition
            optimal_params = await self._get_network_optimal_parameters(
                network_condition, target_platform
            )
            
            # Load and optimize audio
            audio_array, sample_rate = await self._load_audio(audio_data)
            
            # Apply network-specific optimizations
            optimized_audio = await self._apply_network_optimizations(
                audio_array, sample_rate, optimal_params
            )
            
            # Convert to optimal format
            optimized_bytes = await self._convert_to_optimal_format(
                optimized_audio, sample_rate, optimal_params
            )
            
            return {
                'optimized_audio': optimized_bytes,
                'parameters': optimal_params,
                'original_size_mb': len(await self._convert_to_bytes(audio_array, sample_rate)) / (1024 * 1024),
                'optimized_size_mb': len(optimized_bytes) / (1024 * 1024),
                'compression_ratio': len(optimized_bytes) / len(await self._convert_to_bytes(audio_array, sample_rate)),
                'estimated_streaming_time': await self._estimate_streaming_time(optimized_bytes, network_condition)
            }
            
        except Exception as e:
            logger.error(f"Network condition optimization failed: {e}")
            raise
    
    async def _load_audio(self, audio_data: Union[bytes, BinaryIO]) -> Tuple[np.ndarray, int]:
        """Load audio from bytes or file"""
        if isinstance(audio_data, bytes):
            audio_bytes = audio_data
        else:
            audio_bytes = audio_data.read()
            audio_data.seek(0)
        
        if not STREAMING_AVAILABLE:
            # Fallback: return dummy data
            return np.random.randn(44100), 44100
        
        # Create temporary file and load with librosa
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            audio_array, sample_rate = librosa.load(tmp_file.name, sr=None)
            os.unlink(tmp_file.name)
            
            return audio_array, sample_rate
    
    async def _calculate_optimization_parameters(self,
                                               audio: np.ndarray,
                                               sample_rate: int,
                                               settings: StreamingSettings,
                                               platform_profile: StreamingProfile) -> Dict[str, Any]:
        """Calculate optimization parameters"""
        try:
            params = {}
            
            # Analyze audio characteristics
            duration = len(audio) / sample_rate
            rms_level = np.sqrt(np.mean(audio**2))
            peak_level = np.max(np.abs(audio))
            dynamic_range = 20 * np.log10(peak_level / (rms_level + 1e-10))
            
            params['duration'] = duration
            params['dynamic_range'] = dynamic_range
            params['complexity'] = await self._calculate_audio_complexity(audio, sample_rate)
            
            # Network-based parameters
            if settings.network_condition == NetworkCondition.POOR:
                params['aggressive_compression'] = True
                params['quality_priority'] = False
            elif settings.network_condition == NetworkCondition.EXCELLENT:
                params['aggressive_compression'] = False
                params['quality_priority'] = True
            else:
                params['aggressive_compression'] = False
                params['quality_priority'] = settings.optimization_strategy == OptimizationStrategy.QUALITY_PRIORITY
            
            # Platform-specific parameters
            params['target_loudness'] = platform_profile.loudness_target_lufs
            params['max_file_size'] = platform_profile.max_file_size_mb
            
            return params
            
        except Exception as e:
            logger.error(f"Optimization parameter calculation failed: {e}")
            return {}
    
    async def _calculate_audio_complexity(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate audio complexity for optimization decisions"""
        try:
            if not STREAMING_AVAILABLE:
                return 0.5
            
            # Spectral complexity
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            spectral_complexity = np.mean(np.std(magnitude, axis=0))
            
            # Temporal complexity
            rms = librosa.feature.rms(y=audio)[0]
            temporal_complexity = np.std(rms)
            
            # Harmonic complexity
            harmonic, percussive = librosa.effects.hpss(audio)
            harmonic_ratio = np.mean(harmonic**2) / (np.mean(audio**2) + 1e-10)
            
            # Combine complexities
            overall_complexity = (spectral_complexity + temporal_complexity + (1 - harmonic_ratio)) / 3
            
            return min(1.0, overall_complexity)
            
        except Exception as e:
            logger.error(f"Audio complexity calculation failed: {e}")
            return 0.5
    
    async def _preprocess_for_streaming(self,
                                      audio: np.ndarray,
                                      sample_rate: int,
                                      settings: StreamingSettings,
                                      platform_profile: StreamingProfile) -> np.ndarray:
        """Preprocess audio for streaming optimization"""
        try:
            processed_audio = audio.copy()
            
            # Normalize to target loudness
            if platform_profile.loudness_target_lufs:
                processed_audio = await self._normalize_to_lufs(
                    processed_audio, sample_rate, platform_profile.loudness_target_lufs
                )
            
            # Apply dynamic range optimization
            if platform_profile.dynamic_range_target and settings.optimization_strategy != OptimizationStrategy.QUALITY_PRIORITY:
                processed_audio = await self._optimize_dynamic_range(
                    processed_audio, sample_rate, platform_profile.dynamic_range_target
                )
            
            # Apply psychoacoustic optimizations
            if settings.enable_psychoacoustic_optimization:
                processed_audio = await self._apply_psychoacoustic_optimization(
                    processed_audio, sample_rate, settings
                )
            
            return processed_audio
            
        except Exception as e:
            logger.error(f"Streaming preprocessing failed: {e}")
            return audio
    
    async def _normalize_to_lufs(self, audio: np.ndarray, sample_rate: int, target_lufs: float) -> np.ndarray:
        """Normalize audio to target LUFS"""
        try:
            # Simplified LUFS normalization
            current_rms = np.sqrt(np.mean(audio**2))
            if current_rms == 0:
                return audio
            
            current_lufs = -0.691 + 10 * np.log10(current_rms)
            gain_db = target_lufs - current_lufs
            gain_linear = 10**(gain_db / 20)
            
            normalized_audio = audio * gain_linear
            
            # Prevent clipping
            peak = np.max(np.abs(normalized_audio))
            if peak > 0.95:
                normalized_audio = normalized_audio * (0.95 / peak)
            
            return normalized_audio
            
        except Exception as e:
            logger.error(f"LUFS normalization failed: {e}")
            return audio
    
    async def _optimize_dynamic_range(self, audio: np.ndarray, sample_rate: int, target_dr: float) -> np.ndarray:
        """Optimize dynamic range for streaming"""
        try:
            # Calculate current dynamic range
            rms = np.sqrt(np.mean(audio**2))
            peak = np.max(np.abs(audio))
            current_dr = 20 * np.log10(peak / (rms + 1e-10))
            
            if current_dr <= target_dr:
                return audio  # Already within target
            
            # Apply gentle compression to reduce dynamic range
            compression_ratio = current_dr / target_dr
            threshold = rms * 2  # Simple threshold
            
            compressed_audio = audio.copy()
            mask = np.abs(audio) > threshold
            compressed_audio[mask] = threshold + (audio[mask] - threshold) / compression_ratio
            
            return compressed_audio
            
        except Exception as e:
            logger.error(f"Dynamic range optimization failed: {e}")
            return audio
    
    async def _apply_psychoacoustic_optimization(self, audio: np.ndarray, sample_rate: int, settings: StreamingSettings) -> np.ndarray:
        """Apply psychoacoustic optimizations"""
        try:
            # Simple psychoacoustic optimization
            # In production, would use sophisticated perceptual models
            
            if not STREAMING_AVAILABLE:
                return audio
            
            # Apply pre-emphasis for better perceptual encoding
            pre_emphasis = 0.97
            emphasized_audio = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
            
            # Gentle high-frequency enhancement for clarity
            if settings.network_condition in [NetworkCondition.POOR, NetworkCondition.VERY_POOR]:
                # Enhance clarity for low bitrate
                nyquist = sample_rate / 2
                high_freq = 4000 / nyquist
                sos = signal.butter(2, high_freq, btype='high', output='sos')
                high_emphasis = signal.sosfilt(sos, emphasized_audio) * 0.1
                emphasized_audio += high_emphasis
            
            return emphasized_audio
            
        except Exception as e:
            logger.error(f"Psychoacoustic optimization failed: {e}")
            return audio
    
    async def _create_optimized_variant(self,
                                      audio: np.ndarray,
                                      sample_rate: int,
                                      codec: AudioCodec,
                                      bitrate: int,
                                      settings: StreamingSettings,
                                      platform_profile: StreamingProfile,
                                      optimization_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized variant for specific codec and bitrate"""
        try:
            # Apply codec-specific optimizations
            optimized_audio = await self._apply_codec_optimizations(
                audio, sample_rate, codec, bitrate, settings
            )
            
            # Convert to target format
            converted_bytes = await self._convert_to_codec(
                optimized_audio, sample_rate, codec, bitrate
            )
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                audio, optimized_audio, sample_rate
            )
            
            # Estimate streaming performance
            streaming_performance = await self._estimate_streaming_performance(
                converted_bytes, bitrate, settings.network_condition
            )
            
            variant = {
                'success': True,
                'codec': codec.value,
                'bitrate_kbps': bitrate,
                'sample_rate': sample_rate,
                'file_size_bytes': len(converted_bytes),
                'file_size_mb': len(converted_bytes) / (1024 * 1024),
                'audio_data': converted_bytes,
                'quality_metrics': quality_metrics,
                'streaming_performance': streaming_performance,
                'compatibility': await self._check_codec_compatibility(codec, settings.target_platform)
            }
            
            return variant
            
        except Exception as e:
            logger.error(f"Variant creation failed for {codec.value}@{bitrate}kbps: {e}")
            return {
                'success': False,
                'codec': codec.value,
                'bitrate_kbps': bitrate,
                'error': str(e)
            }
    
    async def _apply_codec_optimizations(self,
                                       audio: np.ndarray,
                                       sample_rate: int,
                                       codec: AudioCodec,
                                       bitrate: int,
                                       settings: StreamingSettings) -> np.ndarray:
        """Apply codec-specific optimizations"""
        try:
            optimized_audio = audio.copy()
            
            if codec == AudioCodec.MP3:
                # MP3-specific optimizations
                if bitrate < 192:
                    # Reduce high frequencies for low bitrate MP3
                    nyquist = sample_rate / 2
                    cutoff = min(16000, bitrate * 50) / nyquist  # Adaptive cutoff
                    sos = signal.butter(4, cutoff, btype='low', output='sos')
                    optimized_audio = signal.sosfilt(sos, optimized_audio)
            
            elif codec == AudioCodec.AAC:
                # AAC-specific optimizations
                if bitrate < 128:
                    # Gentle stereo imaging reduction for low bitrate
                    if len(optimized_audio.shape) == 2:
                        mid = np.mean(optimized_audio, axis=0)
                        side = optimized_audio[0] - optimized_audio[1]
                        optimized_audio = np.array([mid + side * 0.7, mid - side * 0.7])
            
            elif codec == AudioCodec.OPUS:
                # OPUS-specific optimizations
                # OPUS handles low bitrates well, minimal preprocessing needed
                pass
            
            return optimized_audio
            
        except Exception as e:
            logger.error(f"Codec optimization failed: {e}")
            return audio
    
    async def _convert_to_codec(self,
                              audio: np.ndarray,
                              sample_rate: int,
                              codec: AudioCodec,
                              bitrate: int) -> bytes:
        """Convert audio to specific codec"""
        try:
            # For now, return WAV format as placeholder
            # In production, would use proper codec libraries
            if STREAMING_AVAILABLE:
                with tempfile.NamedTemporaryFile(suffix=f'.{codec.value}', delete=False) as tmp_file:
                    # Use soundfile for basic conversion
                    sf.write(tmp_file.name, audio, sample_rate)
                    tmp_file.flush()
                    
                    with open(tmp_file.name, 'rb') as f:
                        converted_bytes = f.read()
                    
                    os.unlink(tmp_file.name)
                    return converted_bytes
            else:
                # Fallback
                return (audio * 32767).astype(np.int16).tobytes()
                
        except Exception as e:
            logger.error(f"Codec conversion failed: {e}")
            return (audio * 32767).astype(np.int16).tobytes()
    
    async def _convert_to_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        """Convert audio array to bytes"""
        try:
            if STREAMING_AVAILABLE:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    sf.write(tmp_file.name, audio, sample_rate)
                    tmp_file.flush()
                    
                    with open(tmp_file.name, 'rb') as f:
                        audio_bytes = f.read()
                    
                    os.unlink(tmp_file.name)
                    return audio_bytes
            else:
                return (audio * 32767).astype(np.int16).tobytes()
                
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return (audio * 32767).astype(np.int16).tobytes()
    
    async def _calculate_quality_metrics(self,
                                       original: np.ndarray,
                                       optimized: np.ndarray,
                                       sample_rate: int) -> Dict[str, float]:
        """Calculate quality metrics for optimization"""
        try:
            # Ensure same length
            min_length = min(len(original), len(optimized))
            orig = original[:min_length]
            opt = optimized[:min_length]
            
            # SNR calculation
            signal_power = np.mean(orig**2)
            noise_power = np.mean((orig - opt)**2)
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            
            # Correlation
            correlation = np.corrcoef(orig, opt)[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
            
            # Spectral similarity (if libraries available)
            spectral_similarity = 0.8  # Placeholder
            if STREAMING_AVAILABLE:
                orig_spectrum = np.abs(np.fft.fft(orig))
                opt_spectrum = np.abs(np.fft.fft(opt))
                spectral_similarity = np.corrcoef(orig_spectrum, opt_spectrum)[0, 1]
                if np.isnan(spectral_similarity):
                    spectral_similarity = 0.8
            
            return {
                'snr_db': float(snr),
                'correlation': float(correlation),
                'spectral_similarity': float(spectral_similarity),
                'quality_score': float((snr/40 + correlation + spectral_similarity) / 3)
            }
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return {
                'snr_db': 0.0,
                'correlation': 0.0,
                'spectral_similarity': 0.0,
                'quality_score': 0.0
            }
    
    async def _estimate_streaming_performance(self,
                                            audio_bytes: bytes,
                                            bitrate: int,
                                            network_condition: NetworkCondition) -> Dict[str, Any]:
        """Estimate streaming performance"""
        try:
            file_size_mb = len(audio_bytes) / (1024 * 1024)
            
            # Network bandwidth estimates
            bandwidth_map = {
                NetworkCondition.EXCELLENT: 10000,  # 10 Mbps
                NetworkCondition.GOOD: 5000,        # 5 Mbps
                NetworkCondition.MODERATE: 1000,    # 1 Mbps
                NetworkCondition.POOR: 256,         # 256 Kbps
                NetworkCondition.VERY_POOR: 64      # 64 Kbps
            }
            
            available_bandwidth = bandwidth_map[network_condition]
            
            # Streaming calculations
            transfer_time = (file_size_mb * 8 * 1024) / available_bandwidth  # seconds
            buffer_ratio = available_bandwidth / bitrate
            rebuffer_risk = max(0.0, 1.0 - buffer_ratio)
            
            return {
                'transfer_time_seconds': transfer_time,
                'buffer_ratio': buffer_ratio,
                'rebuffer_risk': rebuffer_risk,
                'suitable_for_network': buffer_ratio > 1.5,
                'estimated_startup_delay': transfer_time * 0.1  # 10% for initial buffer
            }
            
        except Exception as e:
            logger.error(f"Streaming performance estimation failed: {e}")
            return {}
    
    async def _check_codec_compatibility(self, codec: AudioCodec, platform: StreamingPlatform) -> Dict[str, Any]:
        """Check codec compatibility with platform"""
        # Simplified compatibility check
        compatibility_matrix = {
            StreamingPlatform.SPOTIFY: [AudioCodec.AAC, AudioCodec.MP3],
            StreamingPlatform.APPLE_MUSIC: [AudioCodec.AAC, AudioCodec.MP3],
            StreamingPlatform.YOUTUBE: [AudioCodec.AAC, AudioCodec.MP3, AudioCodec.OPUS],
            StreamingPlatform.SOUNDCLOUD: [AudioCodec.AAC, AudioCodec.MP3],
            StreamingPlatform.TWITCH: [AudioCodec.AAC, AudioCodec.MP3],
            StreamingPlatform.DISCORD: [AudioCodec.OPUS, AudioCodec.AAC]
        }
        
        supported_codecs = compatibility_matrix.get(platform, [AudioCodec.AAC, AudioCodec.MP3])
        is_compatible = codec in supported_codecs
        
        return {
            'compatible': is_compatible,
            'platform_supported_codecs': [c.value for c in supported_codecs],
            'recommendation': 'use_as_is' if is_compatible else 'convert_to_compatible_format'
        }
    
    async def _assess_variant_quality(self, variants: List[Dict[str, Any]], 
                                    original_audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Assess quality of all variants"""
        quality_scores = {}
        
        for variant in variants:
            if variant['success']:
                variant_key = f"{variant['codec']}_{variant['bitrate_kbps']}kbps"
                quality_scores[variant_key] = variant['quality_metrics']['quality_score']
        
        # Overall quality assessment
        if quality_scores:
            quality_scores['average_quality'] = np.mean(list(quality_scores.values()))
            quality_scores['best_quality'] = max(quality_scores.values())
            quality_scores['worst_quality'] = min(quality_scores.values())
        
        return quality_scores
    
    async def _calculate_bandwidth_savings(self, variants: List[Dict[str, Any]], 
                                         network_condition: NetworkCondition) -> Dict[str, float]:
        """Calculate bandwidth savings for different variants"""
        bandwidth_savings = {}
        
        # Find reference (highest quality) variant
        reference_size = 0
        for variant in variants:
            if variant['success'] and variant['file_size_mb'] > reference_size:
                reference_size = variant['file_size_mb']
        
        if reference_size == 0:
            return bandwidth_savings
        
        for variant in variants:
            if variant['success']:
                variant_key = f"{variant['codec']}_{variant['bitrate_kbps']}kbps"
                savings_percent = ((reference_size - variant['file_size_mb']) / reference_size) * 100
                bandwidth_savings[variant_key] = max(0.0, savings_percent)
        
        return bandwidth_savings
    
    async def _generate_compatibility_report(self, variants: List[Dict[str, Any]], 
                                           platform: StreamingPlatform) -> Dict[str, Any]:
        """Generate compatibility report"""
        compatible_variants = []
        incompatible_variants = []
        
        for variant in variants:
            if variant['success']:
                if variant['compatibility']['compatible']:
                    compatible_variants.append(variant)
                else:
                    incompatible_variants.append(variant)
        
        return {
            'total_variants': len(variants),
            'compatible_variants': len(compatible_variants),
            'incompatible_variants': len(incompatible_variants),
            'compatibility_rate': len(compatible_variants) / len(variants) if variants else 0,
            'recommended_variants': [v for v in compatible_variants if v['quality_metrics']['quality_score'] > 0.7]
        }
    
    async def _generate_streaming_recommendations(self, variants: List[Dict[str, Any]],
                                                settings: StreamingSettings,
                                                platform_profile: StreamingProfile,
                                                quality_scores: Dict[str, float]) -> List[str]:
        """Generate streaming recommendations"""
        recommendations = []
        
        if not variants:
            recommendations.append("No successful variants created - check input audio quality")
            return recommendations
        
        # Quality recommendations
        avg_quality = quality_scores.get('average_quality', 0)
        if avg_quality < 0.6:
            recommendations.append("Overall quality is low - consider using higher bitrates")
        elif avg_quality > 0.9:
            recommendations.append("Excellent quality achieved - variants ready for streaming")
        
        # Network-specific recommendations
        if settings.network_condition in [NetworkCondition.POOR, NetworkCondition.VERY_POOR]:
            recommendations.append("For poor network conditions, prioritize lower bitrate variants")
            recommendations.append("Consider using OPUS codec for better compression efficiency")
        
        # Platform-specific recommendations
        if settings.target_platform == StreamingPlatform.SPOTIFY:
            recommendations.append("Ensure loudness normalization to -14 LUFS for Spotify")
        elif settings.target_platform == StreamingPlatform.YOUTUBE:
            recommendations.append("Consider multiple bitrate tiers for YouTube adaptive streaming")
        
        # File size recommendations
        large_variants = [v for v in variants if v.get('file_size_mb', 0) > 50]
        if large_variants:
            recommendations.append("Some variants are large - consider more aggressive compression for mobile users")
        
        return recommendations
    
    # Additional methods for adaptive streaming
    
    async def _create_bandwidth_ladder(self, network_condition: NetworkCondition, 
                                     platform_profile: StreamingProfile) -> List[int]:
        """Create bandwidth ladder for adaptive streaming"""
        base_bitrates = platform_profile.bitrate_tiers
        
        # Adjust based on network condition
        if network_condition in [NetworkCondition.POOR, NetworkCondition.VERY_POOR]:
            # Focus on lower bitrates
            ladder = [br for br in base_bitrates if br <= 128]
        elif network_condition == NetworkCondition.EXCELLENT:
            # Include all bitrates
            ladder = base_bitrates
        else:
            # Moderate selection
            ladder = [br for br in base_bitrates if br <= 320]
        
        return sorted(ladder)
    
    async def _segment_audio(self, audio: np.ndarray, sample_rate: int, 
                           segment_duration: float) -> List[np.ndarray]:
        """Segment audio for adaptive streaming"""
        segment_samples = int(segment_duration * sample_rate)
        segments = []
        
        for i in range(0, len(audio), segment_samples):
            segment = audio[i:i + segment_samples]
            if len(segment) > 0:
                segments.append(segment)
        
        return segments
    
    async def _optimize_segment(self, segment: np.ndarray, sample_rate: int,
                              bitrate: int, settings: StreamingSettings,
                              platform_profile: StreamingProfile) -> Dict[str, Any]:
        """Optimize individual segment"""
        try:
            # Apply segment-specific optimizations
            optimized_segment = segment.copy()
            
            # Convert to bytes
            segment_bytes = await self._convert_to_codec(
                optimized_segment, sample_rate, AudioCodec.AAC, bitrate
            )
            
            return {
                'segment_data': segment_bytes,
                'duration': len(segment) / sample_rate,
                'size_bytes': len(segment_bytes),
                'bitrate_kbps': bitrate
            }
            
        except Exception as e:
            logger.error(f"Segment optimization failed: {e}")
            return {}
    
    async def _calculate_switching_points(self, variants: List[Dict[str, Any]],
                                        segments: List[np.ndarray],
                                        bandwidth_ladder: List[int]) -> List[Dict[str, Any]]:
        """Calculate adaptive bitrate switching points"""
        switching_points = []
        
        # Simple switching logic based on segment complexity
        for i, segment in enumerate(segments):
            segment_complexity = await self._calculate_audio_complexity(segment, 44100)
            
            # Choose bitrate based on complexity
            if segment_complexity > 0.8:
                recommended_bitrate = max(bandwidth_ladder)
            elif segment_complexity > 0.5:
                mid_index = len(bandwidth_ladder) // 2
                recommended_bitrate = bandwidth_ladder[mid_index]
            else:
                recommended_bitrate = min(bandwidth_ladder)
            
            switching_points.append({
                'segment_index': i,
                'recommended_bitrate': recommended_bitrate,
                'complexity_score': segment_complexity,
                'timestamp': i * 6.0  # Assuming 6 second segments
            })
        
        return switching_points
    
    async def _generate_adaptive_manifest(self, variants: List[Dict[str, Any]],
                                        segment_duration: float,
                                        platform: StreamingPlatform) -> Dict[str, Any]:
        """Generate adaptive streaming manifest"""
        manifest = {
            'version': '1.0',
            'type': 'adaptive_audio',
            'segment_duration': segment_duration,
            'total_duration': sum(seg['duration'] for seg in variants[0]['segments']) if variants else 0,
            'variants': []
        }
        
        for variant in variants:
            manifest_variant = {
                'bitrate': variant['bitrate_kbps'],
                'codec': variant['codec'],
                'bandwidth': variant['bitrate_kbps'] * 1000,
                'segments': len(variant['segments']),
                'average_segment_size': np.mean([seg['size_bytes'] for seg in variant['segments']]) if variant['segments'] else 0
            }
            manifest['variants'].append(manifest_variant)
        
        return manifest
    
    def _get_network_optimal_parameters(self, network_condition: NetworkCondition,
                                      platform: StreamingPlatform) -> Dict[str, Any]:
        """Get optimal parameters for network condition"""
        network_params = {
            NetworkCondition.EXCELLENT: {
                'max_bitrate': 320,
                'preferred_codec': AudioCodec.AAC,
                'quality_priority': True,
                'compression_level': 'minimal'
            },
            NetworkCondition.GOOD: {
                'max_bitrate': 192,
                'preferred_codec': AudioCodec.AAC,
                'quality_priority': True,
                'compression_level': 'moderate'
            },
            NetworkCondition.MODERATE: {
                'max_bitrate': 128,
                'preferred_codec': AudioCodec.AAC,
                'quality_priority': False,
                'compression_level': 'aggressive'
            },
            NetworkCondition.POOR: {
                'max_bitrate': 64,
                'preferred_codec': AudioCodec.OPUS,
                'quality_priority': False,
                'compression_level': 'maximum'
            },
            NetworkCondition.VERY_POOR: {
                'max_bitrate': 32,
                'preferred_codec': AudioCodec.OPUS,
                'quality_priority': False,
                'compression_level': 'maximum'
            }
        }
        
        return network_params.get(network_condition, network_params[NetworkCondition.MODERATE])
    
    async def _apply_network_optimizations(self, audio: np.ndarray, sample_rate: int,
                                         optimal_params: Dict[str, Any]) -> np.ndarray:
        """Apply network-specific optimizations"""
        optimized_audio = audio.copy()
        
        compression_level = optimal_params.get('compression_level', 'moderate')
        
        if compression_level == 'aggressive':
            # Apply more aggressive preprocessing
            optimized_audio = await self._apply_aggressive_preprocessing(optimized_audio, sample_rate)
        elif compression_level == 'maximum':
            # Apply maximum compression preprocessing
            optimized_audio = await self._apply_maximum_preprocessing(optimized_audio, sample_rate)
        
        return optimized_audio
    
    async def _apply_aggressive_preprocessing(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply aggressive preprocessing for bandwidth-constrained scenarios"""
        try:
            # Reduce bandwidth
            if STREAMING_AVAILABLE:
                nyquist = sample_rate / 2
                cutoff = 8000 / nyquist  # 8 kHz cutoff
                sos = signal.butter(4, cutoff, btype='low', output='sos')
                filtered_audio = signal.sosfilt(sos, audio)
            else:
                filtered_audio = audio
            
            # Apply moderate compression
            threshold = np.std(filtered_audio) * 2
            ratio = 3.0
            compressed_audio = np.where(
                np.abs(filtered_audio) > threshold,
                threshold + (filtered_audio - threshold * np.sign(filtered_audio)) / ratio,
                filtered_audio
            )
            
            return compressed_audio
            
        except Exception as e:
            logger.error(f"Aggressive preprocessing failed: {e}")
            return audio
    
    async def _apply_maximum_preprocessing(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply maximum preprocessing for very poor network conditions"""
        try:
            # Aggressive bandwidth reduction
            if STREAMING_AVAILABLE:
                nyquist = sample_rate / 2
                cutoff = 4000 / nyquist  # 4 kHz cutoff
                sos = signal.butter(6, cutoff, btype='low', output='sos')
                filtered_audio = signal.sosfilt(sos, audio)
            else:
                filtered_audio = audio
            
            # Aggressive compression
            threshold = np.std(filtered_audio) * 1.5
            ratio = 6.0
            compressed_audio = np.where(
                np.abs(filtered_audio) > threshold,
                threshold + (filtered_audio - threshold * np.sign(filtered_audio)) / ratio,
                filtered_audio
            )
            
            # Additional dynamic range reduction
            compressed_audio = np.tanh(compressed_audio * 2) / 2
            
            return compressed_audio
            
        except Exception as e:
            logger.error(f"Maximum preprocessing failed: {e}")
            return audio
    
    async def _convert_to_optimal_format(self, audio: np.ndarray, sample_rate: int,
                                       optimal_params: Dict[str, Any]) -> bytes:
        """Convert to optimal format for network conditions"""
        codec = optimal_params.get('preferred_codec', AudioCodec.AAC)
        bitrate = optimal_params.get('max_bitrate', 128)
        
        return await self._convert_to_codec(audio, sample_rate, codec, bitrate)
    
    async def _estimate_streaming_time(self, audio_bytes: bytes, network_condition: NetworkCondition) -> float:
        """Estimate streaming time for given network condition"""
        bandwidth_map = {
            NetworkCondition.EXCELLENT: 10000,
            NetworkCondition.GOOD: 5000,
            NetworkCondition.MODERATE: 1000,
            NetworkCondition.POOR: 256,
            NetworkCondition.VERY_POOR: 64
        }
        
        bandwidth_kbps = bandwidth_map[network_condition]
        file_size_kb = len(audio_bytes) / 1024
        
        return file_size_kb / bandwidth_kbps  # seconds
    
    def _get_recommended_network_for_bitrate(self, bitrate: int) -> NetworkCondition:
        """Get recommended network condition for bitrate"""
        if bitrate >= 256:
            return NetworkCondition.EXCELLENT
        elif bitrate >= 128:
            return NetworkCondition.GOOD
        elif bitrate >= 64:
            return NetworkCondition.MODERATE
        elif bitrate >= 32:
            return NetworkCondition.POOR
        else:
            return NetworkCondition.VERY_POOR
    
    def _generate_cache_key(self, audio: np.ndarray, settings: StreamingSettings) -> str:
        """Generate cache key for optimization results"""
        audio_hash = hashlib.md5(audio.tobytes()).hexdigest()[:16]
        settings_hash = hashlib.md5(json.dumps(settings.__dict__, sort_keys=True).encode()).hexdigest()[:16]
        return f"{audio_hash}_{settings_hash}"
    
    def _get_default_profile(self) -> StreamingProfile:
        """Get default streaming profile"""
        return StreamingProfile(
            platform=StreamingPlatform.CUSTOM,
            recommended_formats=[AudioCodec.AAC, AudioCodec.MP3],
            bitrate_tiers=[64, 128, 192, 256, 320],
            sample_rates=[44100, 48000],
            max_file_size_mb=None,
            loudness_target_lufs=-14.0,
            dynamic_range_target=12.0,
            special_requirements={}
        )
    
    def _initialize_platform_profiles(self):
        """Initialize streaming platform profiles"""
        self.streaming_profiles = {
            StreamingPlatform.SPOTIFY: StreamingProfile(
                platform=StreamingPlatform.SPOTIFY,
                recommended_formats=[AudioCodec.AAC, AudioCodec.MP3],
                bitrate_tiers=[96, 160, 320],
                sample_rates=[44100],
                max_file_size_mb=None,
                loudness_target_lufs=-14.0,
                dynamic_range_target=None,
                special_requirements={'loudness_normalization': True}
            ),
            
            StreamingPlatform.APPLE_MUSIC: StreamingProfile(
                platform=StreamingPlatform.APPLE_MUSIC,
                recommended_formats=[AudioCodec.AAC],
                bitrate_tiers=[128, 256, 512],
                sample_rates=[44100, 48000],
                max_file_size_mb=None,
                loudness_target_lufs=-16.0,
                dynamic_range_target=None,
                special_requirements={'high_quality_tier': True}
            ),
            
            StreamingPlatform.YOUTUBE: StreamingProfile(
                platform=StreamingPlatform.YOUTUBE,
                recommended_formats=[AudioCodec.AAC, AudioCodec.OPUS],
                bitrate_tiers=[64, 128, 192, 256],
                sample_rates=[44100, 48000],
                max_file_size_mb=None,
                loudness_target_lufs=-14.0,
                dynamic_range_target=10.0,
                special_requirements={'adaptive_streaming': True}
            ),
            
            StreamingPlatform.DISCORD: StreamingProfile(
                platform=StreamingPlatform.DISCORD,
                recommended_formats=[AudioCodec.OPUS],
                bitrate_tiers=[64, 96, 128],
                sample_rates=[48000],
                max_file_size_mb=8.0,
                loudness_target_lufs=-18.0,
                dynamic_range_target=8.0,
                special_requirements={'low_latency': True}
            )
        }
    
    def _load_optimization_models(self):
        """Load streaming optimization models"""
        logger.info("Streaming optimization models loading placeholder")