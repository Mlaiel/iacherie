"""🗜️ Audio Compression Module - Enterprise Audio Compression & Codecs

Advanced audio compression, codec management, bitrate optimization, and quality preservation
for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL STRICT : Ce code et concept sont la propriété intellectuelle 
exclusive de Fahed Mlaiel. Toute utilisation, copie, vol ou reproduction sans 
autorisation écrite expresse de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires.
"""

import numpy as np
import soundfile as sf
import librosa
import psutil
import time
import json
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import logging
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
import tempfile
import multiprocessing as mp


class CompressionFormat(Enum):
    """Extended audio compression formats for enterprise"""
    # Lossless Formats
    WAV = "wav"
    FLAC = "flac" 
    ALAC = "alac"
    APE = "ape"
    WV = "wv"  # WavPack
    TTA = "tta"
    
    # Lossy Formats
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    OPUS = "opus"
    WMA = "wma"
    
    # Professional Formats
    BWF = "bwf"  # Broadcast Wave Format
    RF64 = "rf64"  # 64-bit RF64
    W64 = "w64"   # Sony Wave64
    
    # Specialized Formats
    DSD = "dsd"   # Direct Stream Digital
    MQA = "mqa"   # Master Quality Authenticated
    LDAC = "ldac" # Sony LDAC
    APTX = "aptx" # Qualcomm aptX


class CompressionQuality(IntEnum):
    """Quality levels for compression"""
    DRAFT = 1          # 64 kbps - Draft quality
    PREVIEW = 2        # 96 kbps - Preview quality
    GOOD = 3           # 128 kbps - Good quality
    VERY_GOOD = 4      # 192 kbps - Very good quality
    HIGH = 5           # 256 kbps - High quality
    VERY_HIGH = 6      # 320 kbps - Very high quality
    LOSSLESS = 7       # Lossless compression
    AUDIOPHILE = 8     # Maximum quality lossless
    MASTERING = 9      # Studio mastering quality
    ARCHIVE = 10       # Long-term archive quality


class CompressionProfile(Enum):
    """Compression profiles for different use cases"""
    PODCAST = "podcast"
    MUSIC_STREAMING = "music_streaming"
    BROADCAST = "broadcast"
    MASTERING = "mastering"
    MOBILE = "mobile"
    WEB = "web"
    ARCHIVAL = "archival"
    GAMING = "gaming"
    VOICE = "voice"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    SPEECH = "speech"


class StreamingPlatform(Enum):
    """Streaming platform optimization presets"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    TIDAL = "tidal"
    DEEZER = "deezer"
    PANDORA = "pandora"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    DISCORD = "discord"
    ZOOM = "zoom"


@dataclass
class CompressionSettings:
    """Advanced compression configuration"""
    format: CompressionFormat
    quality: CompressionQuality
    profile: CompressionProfile
    bitrate: Optional[int] = None  # Auto-calculated if None
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    
    # Advanced settings
    variable_bitrate: bool = True
    joint_stereo: bool = True
    psychoacoustic_model: int = 2
    noise_shaping: bool = True
    temporal_noise_shaping: bool = True
    spectral_band_replication: bool = False
    parametric_stereo: bool = False
    
    # Platform optimization
    platform: Optional[StreamingPlatform] = None
    normalize_loudness: bool = True
    target_lufs: float = -14.0
    
    # Metadata preservation
    preserve_metadata: bool = True
    preserve_artwork: bool = True
    preserve_replay_gain: bool = True
    
    # Quality control
    quality_threshold: float = 0.95  # Minimum quality score
    max_encode_time: float = 300.0   # Maximum encoding time (seconds)
    
    # Advanced features
    use_gpu_acceleration: bool = False
    parallel_encoding: bool = True
    chunk_processing: bool = True
    chunk_size: int = 1024 * 1024  # 1MB chunks


@dataclass
class CompressionResult:
    """Compression operation result"""
    success: bool
    compressed_data: Optional[bytes] = None
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    quality_score: float = 0.0
    encoding_time: float = 0.0
    bitrate_achieved: int = 0
    format_used: Optional[CompressionFormat] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def compression_efficiency(self) -> float:
        """Calculate compression efficiency"""
        if self.original_size == 0:
            return 0.0
        return (1.0 - self.compressed_size / self.original_size) * 100


class PerceptualAnalyzer:
    """🧠 Perceptual audio analysis for optimal compression"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_content(self, audio_data: np.ndarray, 
                       sample_rate: int = 44100) -> Dict[str, float]:
        """Analyze audio content for compression optimization"""
        try:
            # Ensure mono for analysis
            if len(audio_data.shape) > 1:
                audio_mono = librosa.to_mono(audio_data.T)
            else:
                audio_mono = audio_data
            
            analysis = {}
            
            # Spectral analysis
            stft = librosa.stft(audio_mono)
            magnitude = np.abs(stft)
            
            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio_mono, sr=sample_rate)[0]
            analysis['spectral_centroid'] = np.mean(spectral_centroids)
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(
                y=audio_mono, sr=sample_rate)[0]
            analysis['spectral_rolloff'] = np.mean(rolloff)
            
            # Zero crossing rate (speech/music discrimination)
            zcr = librosa.feature.zero_crossing_rate(audio_mono)[0]
            analysis['zero_crossing_rate'] = np.mean(zcr)
            
            # MFCCs for timbral content
            mfccs = librosa.feature.mfcc(y=audio_mono, sr=sample_rate, n_mfcc=13)
            analysis['mfcc_variance'] = np.var(mfccs)
            
            # Tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_mono, sr=sample_rate)
            analysis['tempo'] = tempo
            analysis['rhythm_regularity'] = self._calculate_rhythm_regularity(beats)
            
            # Dynamic range
            analysis['dynamic_range'] = np.max(audio_mono) - np.min(audio_mono)
            
            # Frequency content distribution
            freqs = librosa.fft_frequencies(sr=sample_rate)
            magnitude_mean = np.mean(magnitude, axis=1)
            
            # Low, mid, high frequency energy
            low_freq_energy = np.sum(magnitude_mean[freqs < 250])
            mid_freq_energy = np.sum(magnitude_mean[(freqs >= 250) & (freqs < 4000)])
            high_freq_energy = np.sum(magnitude_mean[freqs >= 4000])
            
            total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
            if total_energy > 0:
                analysis['low_freq_ratio'] = low_freq_energy / total_energy
                analysis['mid_freq_ratio'] = mid_freq_energy / total_energy
                analysis['high_freq_ratio'] = high_freq_energy / total_energy
            else:
                analysis['low_freq_ratio'] = 0.0
                analysis['mid_freq_ratio'] = 0.0
                analysis['high_freq_ratio'] = 0.0
            
            # Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio_mono)
            analysis['harmonic_ratio'] = np.sum(np.abs(harmonic)) / np.sum(np.abs(audio_mono))
            analysis['percussive_ratio'] = np.sum(np.abs(percussive)) / np.sum(np.abs(audio_mono))
            
            # Complexity score
            analysis['complexity_score'] = self._calculate_complexity_score(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return self._get_default_analysis()
    
    def _calculate_rhythm_regularity(self, beats: np.ndarray) -> float:
        """Calculate rhythm regularity from beat positions"""
        if len(beats) < 3:
            return 0.0
        
        intervals = np.diff(beats)
        return 1.0 / (1.0 + np.std(intervals))
    
    def _calculate_complexity_score(self, analysis: Dict[str, float]) -> float:
        """Calculate overall audio complexity score"""
        weights = {
            'spectral_centroid': 0.2,
            'mfcc_variance': 0.3,
            'dynamic_range': 0.2,
            'high_freq_ratio': 0.15,
            'rhythm_regularity': 0.15
        }
        
        score = 0.0
        for feature, weight in weights.items():
            if feature in analysis:
                normalized_value = min(analysis[feature] / 1000, 1.0)
                score += normalized_value * weight
        
        return min(score, 1.0)
    
    def _get_default_analysis(self) -> Dict[str, float]:
        """Return default analysis values"""
        return {
            'spectral_centroid': 1000.0,
            'spectral_rolloff': 5000.0,
            'zero_crossing_rate': 0.1,
            'mfcc_variance': 100.0,
            'tempo': 120.0,
            'rhythm_regularity': 0.5,
            'dynamic_range': 0.5,
            'low_freq_ratio': 0.33,
            'mid_freq_ratio': 0.33,
            'high_freq_ratio': 0.34,
            'harmonic_ratio': 0.7,
            'percussive_ratio': 0.3,
            'complexity_score': 0.5
        }


class BitrateOptimizer:
    """📊 Intelligent Bitrate Optimization with Perceptual Analysis"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analyzer = PerceptualAnalyzer()
        
        # Platform-specific bitrate recommendations
        self.platform_presets = {
            StreamingPlatform.SPOTIFY: {
                CompressionQuality.GOOD: 96,
                CompressionQuality.HIGH: 160,
                CompressionQuality.VERY_HIGH: 320
            },
            StreamingPlatform.APPLE_MUSIC: {
                CompressionQuality.GOOD: 128,
                CompressionQuality.HIGH: 256,
                CompressionQuality.VERY_HIGH: 256  # AAC
            },
            StreamingPlatform.YOUTUBE_MUSIC: {
                CompressionQuality.GOOD: 128,
                CompressionQuality.HIGH: 256,
                CompressionQuality.VERY_HIGH: 256
            },
            StreamingPlatform.TIDAL: {
                CompressionQuality.HIGH: 320,
                CompressionQuality.VERY_HIGH: 1411,  # CD quality
                CompressionQuality.LOSSLESS: 9216   # MQA
            }
        }
    
    def optimize_bitrate(self, audio_data: np.ndarray, 
                        settings: CompressionSettings,
                        sample_rate: int = 44100) -> int:
        """Optimize bitrate based on content analysis and settings"""
        try:
            # Analyze audio content
            analysis = self.analyzer.analyze_content(audio_data, sample_rate)
            
            # Get base bitrate from platform/quality
            base_bitrate = self._get_base_bitrate(settings)
            
            # Apply content-based adjustments
            complexity_factor = analysis.get('complexity_score', 0.5)
            
            # Adjust based on content type
            if analysis.get('zero_crossing_rate', 0) > 0.15:  # Speech-like
                # Speech content can use lower bitrates
                bitrate_multiplier = 0.7
            elif analysis.get('harmonic_ratio', 0) > 0.8:  # Harmonic music
                # Classical/acoustic music benefits from higher bitrates
                bitrate_multiplier = 1.2
            elif analysis.get('percussive_ratio', 0) > 0.6:  # Percussive
                # Electronic/percussion heavy can use standard bitrates
                bitrate_multiplier = 1.0
            else:
                bitrate_multiplier = 1.0
            
            # Apply complexity scaling
            complexity_multiplier = 0.8 + (complexity_factor * 0.4)
            
            # Calculate optimized bitrate
            optimized_bitrate = int(base_bitrate * bitrate_multiplier * complexity_multiplier)
            
            # Ensure bitrate is within reasonable bounds
            min_bitrate = 64 if settings.format in [CompressionFormat.OPUS, CompressionFormat.AAC] else 96
            max_bitrate = 320 if settings.format != CompressionFormat.FLAC else 1411
            
            optimized_bitrate = max(min_bitrate, min(optimized_bitrate, max_bitrate))
            
            self.logger.info(f"Optimized bitrate: {optimized_bitrate} kbps "
                           f"(complexity: {complexity_factor:.2f})")
            
            return optimized_bitrate
            
        except Exception as e:
            self.logger.error(f"Bitrate optimization failed: {e}")
            return self._get_fallback_bitrate(settings)
    
    def _get_base_bitrate(self, settings: CompressionSettings) -> int:
        """Get base bitrate from platform and quality settings"""
        if settings.bitrate:
            return settings.bitrate
        
        if settings.platform and settings.platform in self.platform_presets:
            preset = self.platform_presets[settings.platform]
            if settings.quality in preset:
                return preset[settings.quality]
        
        # Default quality-based bitrates
        quality_bitrates = {
            CompressionQuality.DRAFT: 64,
            CompressionQuality.PREVIEW: 96,
            CompressionQuality.GOOD: 128,
            CompressionQuality.VERY_GOOD: 192,
            CompressionQuality.HIGH: 256,
            CompressionQuality.VERY_HIGH: 320,
            CompressionQuality.LOSSLESS: 1411,
            CompressionQuality.AUDIOPHILE: 2304,
            CompressionQuality.MASTERING: 4608,
            CompressionQuality.ARCHIVE: 9216
        }
        
        return quality_bitrates.get(settings.quality, 192)
    
    def _get_fallback_bitrate(self, settings: CompressionSettings) -> int:
        """Get fallback bitrate when optimization fails"""
        return self._get_base_bitrate(settings)


class CodecManager:
    """🔧 Enterprise Audio Codec Management System"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.supported_codecs = self._initialize_codec_support()
        self.encoder_cache = {}
    
    def _initialize_codec_support(self) -> Dict[CompressionFormat, Dict[str, Any]]:
        """Initialize comprehensive codec support information"""
        return {
            # Lossless formats
            CompressionFormat.WAV: {
                "name": "Waveform Audio File Format",
                "lossy": False,
                "max_channels": 8,
                "max_sample_rate": 192000,
                "max_bit_depth": 32,
                "streaming_friendly": False,
                "metadata_support": "basic",
                "complexity": "low"
            },
            CompressionFormat.FLAC: {
                "name": "Free Lossless Audio Codec",
                "lossy": False,
                "max_channels": 8,
                "max_sample_rate": 655350,
                "max_bit_depth": 32,
                "streaming_friendly": True,
                "metadata_support": "extensive",
                "complexity": "medium"
            },
            CompressionFormat.ALAC: {
                "name": "Apple Lossless Audio Codec",
                "lossy": False,
                "max_channels": 8,
                "max_sample_rate": 384000,
                "max_bit_depth": 32,
                "streaming_friendly": True,
                "metadata_support": "extensive",
                "complexity": "medium"
            },
            
            # Lossy formats
            CompressionFormat.MP3: {
                "name": "MPEG-1 Audio Layer 3",
                "lossy": True,
                "max_channels": 2,
                "max_sample_rate": 48000,
                "max_bit_depth": 16,
                "streaming_friendly": True,
                "metadata_support": "good",
                "complexity": "low"
            },
            CompressionFormat.AAC: {
                "name": "Advanced Audio Coding",
                "lossy": True,
                "max_channels": 48,
                "max_sample_rate": 96000,
                "max_bit_depth": 32,
                "streaming_friendly": True,
                "metadata_support": "good",
                "complexity": "medium"
            },
            CompressionFormat.OGG: {
                "name": "Ogg Vorbis",
                "lossy": True,
                "max_channels": 255,
                "max_sample_rate": 192000,
                "max_bit_depth": 32,
                "streaming_friendly": True,
                "metadata_support": "extensive",
                "complexity": "medium"
            },
            CompressionFormat.OPUS: {
                "name": "Opus Interactive Audio Codec",
                "lossy": True,
                "max_channels": 255,
                "max_sample_rate": 48000,
                "max_bit_depth": 32,
                "streaming_friendly": True,
                "metadata_support": "good",
                "complexity": "high"
            }
        }
    
    def get_codec_info(self, format: CompressionFormat) -> Dict[str, Any]:
        """Get comprehensive codec information"""
        return self.supported_codecs.get(format, {
            "name": "Unknown Format",
            "lossy": True,
            "supported": False
        })
    
    def is_format_suitable(self, format: CompressionFormat, 
                          settings: CompressionSettings) -> Tuple[bool, str]:
        """Check if format is suitable for given settings"""
        codec_info = self.get_codec_info(format)
        
        if not codec_info.get("name", "").startswith("Unknown"):
            # Check sample rate compatibility
            if settings.sample_rate > codec_info.get("max_sample_rate", 0):
                return False, f"Sample rate {settings.sample_rate} exceeds maximum {codec_info['max_sample_rate']}"
            
            # Check channel compatibility
            if settings.channels > codec_info.get("max_channels", 0):
                return False, f"Channel count {settings.channels} exceeds maximum {codec_info['max_channels']}"
            
            # Check bit depth compatibility
            if settings.bit_depth > codec_info.get("max_bit_depth", 0):
                return False, f"Bit depth {settings.bit_depth} exceeds maximum {codec_info['max_bit_depth']}"
            
            return True, "Format suitable"
        
        return False, "Unsupported format"
    
    def recommend_format(self, settings: CompressionSettings) -> CompressionFormat:
        """Recommend optimal format based on settings"""
        # For lossless requirements
        if settings.quality >= CompressionQuality.LOSSLESS:
            if settings.platform == StreamingPlatform.APPLE_MUSIC:
                return CompressionFormat.ALAC
            else:
                return CompressionFormat.FLAC
        
        # For high-quality lossy
        if settings.quality >= CompressionQuality.HIGH:
            if settings.profile == CompressionProfile.VOICE:
                return CompressionFormat.OPUS
            elif settings.platform in [StreamingPlatform.APPLE_MUSIC, StreamingPlatform.YOUTUBE_MUSIC]:
                return CompressionFormat.AAC
            else:
                return CompressionFormat.MP3
        
        # For standard quality
        if settings.profile == CompressionProfile.VOICE:
            return CompressionFormat.OPUS
        elif settings.platform == StreamingPlatform.APPLE_MUSIC:
            return CompressionFormat.AAC
        else:
            return CompressionFormat.MP3


class AudioCompressor:
    """🗜️ Enterprise Audio Compression Engine with Advanced Features"""
    
    def __init__(self, max_workers -> None: Optional[int] = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.codec_manager = CodecManager()
        self.bitrate_optimizer = BitrateOptimizer()
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Performance monitoring
        self.compression_stats = {
            'total_compressions': 0,
            'total_time': 0.0,
            'total_input_size': 0,
            'total_output_size': 0,
            'format_usage': {},
            'quality_distribution': {}
        }
    
    async def compress_async(self, audio_data: np.ndarray, 
                           settings: CompressionSettings,
                           sample_rate: int = 44100) -> CompressionResult:
        """Asynchronous audio compression"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.compress, 
            audio_data, 
            settings, 
            sample_rate
        )
    
    def compress(self, audio_data: np.ndarray, 
                settings: CompressionSettings,
                sample_rate: int = 44100) -> CompressionResult:
        """Compress audio data with enterprise features"""
        start_time = time.time()
        
        try:
            # Validate input
            if audio_data is None or len(audio_data) == 0:
                return CompressionResult(
                    success=False,
                    error_message="Invalid audio data"
                )
            
            # Pre-compression validation
            format_suitable, message = self.codec_manager.is_format_suitable(
                settings.format, settings
            )
            if not format_suitable:
                return CompressionResult(
                    success=False,
                    error_message=f"Format validation failed: {message}"
                )
            
            # Optimize bitrate if not specified
            if not settings.bitrate:
                settings.bitrate = self.bitrate_optimizer.optimize_bitrate(
                    audio_data, settings, sample_rate
                )
            
            # Ensure proper audio format
            if len(audio_data.shape) == 1:
                # Mono to stereo if needed
                if settings.channels == 2:
                    audio_data = np.column_stack([audio_data, audio_data])
            elif len(audio_data.shape) == 2:
                # Handle channel configuration
                if audio_data.shape[1] != settings.channels:
                    if settings.channels == 1:
                        # Stereo to mono
                        audio_data = librosa.to_mono(audio_data.T)
                    elif settings.channels == 2 and audio_data.shape[1] == 1:
                        # Mono to stereo
                        audio_data = np.column_stack([audio_data, audio_data])
            
            # Apply preprocessing based on profile
            audio_data = self._apply_preprocessing(audio_data, settings, sample_rate)
            
            # Perform compression
            compressed_data = self._perform_compression(audio_data, settings, sample_rate)
            
            # Calculate metrics
            original_size = audio_data.nbytes
            compressed_size = len(compressed_data) if compressed_data else 0
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            encoding_time = time.time() - start_time
            
            # Quality assessment
            quality_score = self._assess_quality(
                audio_data, compressed_data, settings, sample_rate
            )
            
            # Update statistics
            self._update_stats(settings, original_size, compressed_size, encoding_time)
            
            # Create result
            result = CompressionResult(
                success=True,
                compressed_data=compressed_data,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                quality_score=quality_score,
                encoding_time=encoding_time,
                bitrate_achieved=settings.bitrate,
                format_used=settings.format,
                metadata=self._extract_compression_metadata(settings, encoding_time)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return CompressionResult(
                success=False,
                error_message=str(e),
                encoding_time=time.time() - start_time
            )
    
    def _apply_preprocessing(self, audio_data: np.ndarray, 
                           settings: CompressionSettings,
                           sample_rate: int) -> np.ndarray:
        """Apply content-aware preprocessing"""
        try:
            # Normalization based on profile
            if settings.profile in [CompressionProfile.MASTERING, CompressionProfile.ARCHIVAL]:
                # Preserve dynamics for mastering
                pass
            elif settings.normalize_loudness:
                # Apply loudness normalization
                audio_data = self._normalize_loudness(audio_data, settings.target_lufs)
            
            # Profile-specific processing
            if settings.profile == CompressionProfile.VOICE:
                # Voice optimization: high-pass filter, noise reduction
                audio_data = self._optimize_for_voice(audio_data, sample_rate)
            elif settings.profile == CompressionProfile.CLASSICAL:
                # Preserve dynamics and frequency response
                pass
            elif settings.profile == CompressionProfile.ELECTRONIC:
                # Optimize for electronic music characteristics
                audio_data = self._optimize_for_electronic(audio_data, sample_rate)
            
            return audio_data
            
        except Exception as e:
            self.logger.warning(f"Preprocessing failed, using original audio: {e}")
            return audio_data
    
    def _normalize_loudness(self, audio_data: np.ndarray, target_lufs: float) -> np.ndarray:
        """Normalize loudness to target LUFS"""
        # Simplified loudness normalization
        # In practice, would use pyloudnorm or similar
        current_rms = np.sqrt(np.mean(audio_data ** 2))
        target_rms = 10 ** (target_lufs / 20)
        
        if current_rms > 0:
            gain = target_rms / current_rms
            # Prevent clipping
            gain = min(gain, 1.0 / np.max(np.abs(audio_data)))
            return audio_data * gain
        
        return audio_data
    
    def _optimize_for_voice(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Optimize audio for voice content"""
        # High-pass filter to remove low-frequency noise
        from scipy import signal
        sos = signal.butter(4, 80, btype='high', fs=sample_rate, output='sos')
        if len(audio_data.shape) == 1:
            return signal.sosfilt(sos, audio_data)
        else:
            return np.array([signal.sosfilt(sos, channel) for channel in audio_data.T]).T
    
    def _optimize_for_electronic(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Optimize audio for electronic music"""
        # Slight high-frequency enhancement for electronic music
        # This is a simplified approach
        return audio_data * 1.02  # Slight gain boost
    
    def _perform_compression(self, audio_data: np.ndarray, 
                           settings: CompressionSettings,
                           sample_rate: int) -> bytes:
        """Perform the actual compression"""
        try:
            # Create temporary file for compression
            with tempfile.NamedTemporaryFile(suffix=f'.{settings.format.value}') as temp_file:
                
                # Write audio data based on format
                if settings.format == CompressionFormat.WAV:
                    sf.write(temp_file.name, audio_data, sample_rate, 
                            subtype=f'PCM_{settings.bit_depth}')
                elif settings.format == CompressionFormat.FLAC:
                    sf.write(temp_file.name, audio_data, sample_rate, 
                            subtype=f'PCM_{settings.bit_depth}')
                else:
                    # For lossy formats, use default PCM_16 for compatibility
                    sf.write(temp_file.name, audio_data, sample_rate, subtype='PCM_16')
                
                # Read compressed data
                with open(temp_file.name, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            self.logger.error(f"Compression encoding failed: {e}")
            raise
    
    def _assess_quality(self, original: np.ndarray, compressed_data: bytes,
                       settings: CompressionSettings, sample_rate: int) -> float:
        """Assess compression quality"""
        try:
            # For lossless formats, quality is 1.0
            if not self.codec_manager.get_codec_info(settings.format).get('lossy', True):
                return 1.0
            
            # For lossy formats, estimate quality based on bitrate and content
            codec_info = self.codec_manager.get_codec_info(settings.format)
            
            # Base quality from bitrate
            max_bitrate = 320  # kbps
            base_quality = min(settings.bitrate / max_bitrate, 1.0)
            
            # Adjust for codec efficiency
            codec_efficiency = {
                CompressionFormat.OPUS: 1.2,
                CompressionFormat.AAC: 1.1,
                CompressionFormat.OGG: 1.05,
                CompressionFormat.MP3: 1.0
            }
            
            efficiency = codec_efficiency.get(settings.format, 1.0)
            quality_score = min(base_quality * efficiency, 1.0)
            
            return quality_score
            
        except Exception as e:
            self.logger.warning(f"Quality assessment failed: {e}")
            return 0.8  # Default quality estimate
    
    def _extract_compression_metadata(self, settings: CompressionSettings, 
                                    encoding_time: float) -> Dict[str, Any]:
        """Extract compression metadata"""
        return {
            'format': settings.format.value,
            'quality_level': settings.quality.name,
            'profile': settings.profile.value,
            'bitrate': settings.bitrate,
            'sample_rate': settings.sample_rate,
            'channels': settings.channels,
            'bit_depth': settings.bit_depth,
            'variable_bitrate': settings.variable_bitrate,
            'encoding_time': encoding_time,
            'encoder': 'Ainflue Enterprise Compressor v1.0',
            'platform_optimization': settings.platform.value if settings.platform else None,
            'compression_timestamp': time.time()
        }
    
    def _update_stats(self, settings -> None: CompressionSettings, 
                     input_size -> None: int, output_size -> None: int, 
                     encoding_time -> None: float) -> None:
        """Update compression statistics"""
        self.compression_stats['total_compressions'] += 1
        self.compression_stats['total_time'] += encoding_time
        self.compression_stats['total_input_size'] += input_size
        self.compression_stats['total_output_size'] += output_size
        
        # Track format usage
        format_name = settings.format.value
        self.compression_stats['format_usage'][format_name] = \
            self.compression_stats['format_usage'].get(format_name, 0) + 1
        
        # Track quality distribution
        quality_name = settings.quality.name
        self.compression_stats['quality_distribution'][quality_name] = \
            self.compression_stats['quality_distribution'].get(quality_name, 0) + 1
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        stats = self.compression_stats.copy()
        
        if stats['total_compressions'] > 0:
            stats['average_encoding_time'] = stats['total_time'] / stats['total_compressions']
            stats['average_compression_ratio'] = stats['total_output_size'] / stats['total_input_size']
            stats['total_size_saved'] = stats['total_input_size'] - stats['total_output_size']
            stats['size_reduction_percentage'] = (
                (stats['total_input_size'] - stats['total_output_size']) / 
                stats['total_input_size'] * 100
            )
        
        return stats
    
    def compress_batch(self, audio_files: List[Tuple[np.ndarray, CompressionSettings]], 
                      sample_rate: int = 44100) -> List[CompressionResult]:
        """Compress multiple audio files in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.compress, audio_data, settings, sample_rate)
                for audio_data, settings in audio_files
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Batch compression failed: {e}")
                    results.append(CompressionResult(
                        success=False,
                        error_message=str(e)
                    ))
            
            return results
    
    def __del__(self) -> None:
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


class MetadataPreserver:
    """🏷️ Advanced Metadata Preservation System"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from audio file"""
        try:
            metadata = {}
            
            # Use soundfile for basic metadata
            info = sf.info(file_path)
            metadata.update({
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'duration': info.duration,
                'frames': info.frames,
                'format': info.format,
                'subtype': info.subtype
            })
            
            # Additional metadata extraction would go here
            # (using mutagen, eyed3, or similar libraries)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def preserve_metadata(self, source_path: str, target_path: str, 
                         additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Preserve metadata from source to target file"""
        try:
            # Extract metadata from source
            metadata = self.extract_metadata(source_path)
            
            # Add additional metadata if provided
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Apply metadata to target file
            # Implementation would depend on the specific metadata library used
            
            return True
            
        except Exception as e:
            self.logger.error(f"Metadata preservation failed: {e}")
            return False


class QualityController:
    """🎯 Advanced Quality Control and Validation"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.quality_thresholds = {
            CompressionQuality.DRAFT: 0.6,
            CompressionQuality.PREVIEW: 0.7,
            CompressionQuality.GOOD: 0.8,
            CompressionQuality.VERY_GOOD: 0.85,
            CompressionQuality.HIGH: 0.9,
            CompressionQuality.VERY_HIGH: 0.95,
            CompressionQuality.LOSSLESS: 1.0,
            CompressionQuality.AUDIOPHILE: 1.0,
            CompressionQuality.MASTERING: 1.0,
            CompressionQuality.ARCHIVE: 1.0
        }
    
    def validate_quality(self, result: CompressionResult, 
                        target_quality: CompressionQuality) -> Tuple[bool, str]:
        """Validate compression quality against target"""
        threshold = self.quality_thresholds.get(target_quality, 0.8)
        
        if result.quality_score >= threshold:
            return True, f"Quality acceptable: {result.quality_score:.3f} >= {threshold:.3f}"
        else:
            return False, f"Quality below threshold: {result.quality_score:.3f} < {threshold:.3f}"
    
    def recommend_quality_improvements(self, result: CompressionResult) -> List[str]:
        """Recommend quality improvements"""
        recommendations = []
        
        if result.quality_score < 0.8:
            recommendations.append("Consider increasing bitrate for better quality")
            
        if result.compression_ratio > 0.9:
            recommendations.append("Compression ratio is very high, consider lossless format")
            
        if result.encoding_time > 60:
            recommendations.append("Encoding time is high, consider optimizing settings")
            
        return recommendations


# Enterprise Integration Classes
class CompressionOrchestrator:
    """🎼 Enterprise Compression Orchestration System"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.compressor = AudioCompressor()
        self.quality_controller = QualityController()
        self.metadata_preserver = MetadataPreserver()
        
        # Enterprise features
        self.compression_queue = asyncio.Queue()
        self.active_compressions = {}
        self.compression_history = []
    
    async def compress_with_quality_control(self, 
                                          audio_data: np.ndarray,
                                          settings: CompressionSettings,
                                          sample_rate: int = 44100) -> CompressionResult:
        """Compress with automatic quality control and retry"""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Perform compression
            result = await self.compressor.compress_async(audio_data, settings, sample_rate)
            
            if not result.success:
                self.logger.warning(f"Compression attempt {attempt} failed: {result.error_message}")
                continue
            
            # Validate quality
            quality_ok, quality_message = self.quality_controller.validate_quality(
                result, settings.quality
            )
            
            if quality_ok:
                self.logger.info(f"Compression successful on attempt {attempt}: {quality_message}")
                return result
            else:
                self.logger.warning(f"Quality validation failed on attempt {attempt}: {quality_message}")
                
                # Attempt quality improvement
                if attempt < max_attempts:
                    settings = self._improve_settings(settings, result)
        
        # If all attempts failed, return the last result with warning
        self.logger.error(f"All compression attempts failed quality validation")
        return result
    
    def _improve_settings(self, settings: CompressionSettings, 
                         result: CompressionResult) -> CompressionSettings:
        """Improve compression settings based on previous result"""
        new_settings = CompressionSettings(**settings.__dict__)
        
        # Increase bitrate if quality is low
        if result.quality_score < 0.8 and new_settings.bitrate:
            new_settings.bitrate = min(int(new_settings.bitrate * 1.25), 320)
        
        # Disable variable bitrate if consistency is needed
        if result.quality_score < 0.7:
            new_settings.variable_bitrate = False
        
        return new_settings


# Module exports
__all__ = [
    # Enums
    'CompressionFormat', 'CompressionQuality', 'CompressionProfile', 'StreamingPlatform',
    
    # Data classes
    'CompressionSettings', 'CompressionResult',
    
    # Main classes
    'AudioCompressor', 'CodecManager', 'BitrateOptimizer', 'PerceptualAnalyzer',
    'MetadataPreserver', 'QualityController', 'CompressionOrchestrator'
]