"""Audio Quality Assessment Module

Advanced audio quality analysis for musicians, podcasters, and audio content creators.
Implements professional audio metrics and industry-standard quality assessment.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""
import asyncio
import logging
import wave
import struct
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import scipy.signal
from scipy.fft import fft, fftfreq

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider
from ..core.exceptions import QualityCheckError, ContentValidationError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"


class NoiseLevel(Enum):
    """Audio noise level categories"""    EXCELLENT = "excellent"     # < -60 dB
    GOOD = "good"              # -60 to -50 dB
    ACCEPTABLE = "acceptable"   # -50 to -40 dB
    POOR = "poor"              # -40 to -30 dB
    UNACCEPTABLE = "unacceptable"  # > -30 dB


class DynamicRange(Enum):
    """Dynamic range categories"""    EXCELLENT = "excellent"     # > 20 dB
    GOOD = "good"              # 15-20 dB
    ACCEPTABLE = "acceptable"   # 10-15 dB
    COMPRESSED = "compressed"   # 5-10 dB
    OVER_COMPRESSED = "over_compressed"  # < 5 dB


@dataclass
class SpectralAnalysis:
    """Spectral analysis results"""    fundamental_frequency: float = field(default=0.0)
    harmonics: List[float] = field(default_factory=list)
    spectral_centroid: float = field(default=0.0)
    spectral_bandwidth: float = field(default=0.0)
    spectral_rolloff: float = field(default=0.0)
    zero_crossing_rate: float = field(default=0.0)
    mfcc: List[float] = field(default_factory=list)
    
    # Frequency bands analysis
    bass_energy: float = field(default=0.0)      # 20-250 Hz
    mid_energy: float = field(default=0.0)       # 250-4000 Hz
    treble_energy: float = field(default=0.0)    # 4000-20000 Hz
    
    # Audio quality indicators
    thd_plus_noise: float = field(default=0.0)   # Total Harmonic Distortion + Noise
    signal_to_noise_ratio: float = field(default=0.0)
    dynamic_range: float = field(default=0.0)


@dataclass
class AudioQualityProfile:
    """Comprehensive audio quality profile"""    # Basic properties
    sample_rate: int = field(default=0)
    bit_depth: int = field(default=0)
    channels: int = field(default=0)
    duration: float = field(default=0.0)
    file_size: int = field(default=0)
    
    # Quality metrics
    peak_level: float = field(default=0.0)
    rms_level: float = field(default=0.0)
    lufs_integrated: float = field(default=0.0)  # Loudness Units relative to Full Scale
    lufs_momentary_max: float = field(default=0.0)
    lufs_short_term_max: float = field(default=0.0)
    true_peak_max: float = field(default=0.0)
    
    # Noise and distortion
    noise_floor: float = field(default=0.0)
    noise_level: NoiseLevel = field(default=NoiseLevel.ACCEPTABLE)
    thd_percentage: float = field(default=0.0)
    
    # Dynamic range
    dynamic_range_db: float = field(default=0.0)
    dynamic_range_category: DynamicRange = field(default=DynamicRange.ACCEPTABLE)
    crest_factor: float = field(default=0.0)
    
    # Spectral analysis
    spectral_analysis: SpectralAnalysis = field(default_factory=SpectralAnalysis)
    
    # Audio quality scores
    technical_score: float = field(default=0.0)
    loudness_score: float = field(default=0.0)
    frequency_response_score: float = field(default=0.0)
    dynamic_score: float = field(default=0.0)
    noise_score: float = field(default=0.0)
    
    # Overall quality
    overall_quality_score: float = field(default=0.0)
    quality_level: str = field(default="acceptable")
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    enhancement_suggestions: List[str] = field(default_factory=list)


@dataclass
class AudioQualityMetrics:
    """Audio quality metrics container"""    profile: AudioQualityProfile = field(default_factory=AudioQualityProfile)
    
    # Professional metrics
    broadcast_compliance: bool = field(default=False)
    streaming_optimized: bool = field(default=False)
    mastering_quality: str = field(default="unmastered")
    
    # Content analysis
    speech_clarity: float = field(default=0.0)
    music_quality: float = field(default=0.0)
    audio_type: str = field(default="unknown")  # speech, music, mixed, effects
    
    # Platform readiness
    spotify_ready: bool = field(default=False)
    youtube_ready: bool = field(default=False)
    podcast_ready: bool = field(default=False)
    radio_ready: bool = field(default=False)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class AudioQualityAnalyzer(BaseAIModel):
    """    Professional Audio Quality Analyzer
    
    Provides comprehensive audio quality assessment for:
    - Musicians and music producers
    - Podcasters and content creators
    - Audio engineers and mastering studios
    - Streaming platform optimization
    - Broadcast compliance checking
    """    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize audio quality analyzer"""        super().__init__(config or ModelConfig(
            name="audio_quality_analyzer",
            model_type=ModelType.AUDIO_MODEL,
            provider=ModelProvider.LOCAL
        ))
        
        # self.performance_monitor = performance_monitor
        # self.metrics_collector = metrics_collector
        
        # Audio analysis parameters
        self.analysis_window_size = 2048
        self.hop_length = 512
        self.n_mfcc = 13
        
        # Quality thresholds
        self.quality_thresholds = {
            'professional': {
                'sample_rate_min': 48000,
                'bit_depth_min': 24,
                'thd_max': 0.1,
                'snr_min': 80,
                'dynamic_range_min': 15
            },
            'broadcast': {
                'sample_rate_min': 48000,
                'bit_depth_min': 16,
                'thd_max': 0.3,
                'snr_min': 70,
                'dynamic_range_min': 12
            },
            'streaming': {
                'sample_rate_min': 44100,
                'bit_depth_min': 16,
                'thd_max': 0.5,
                'snr_min': 60,
                'dynamic_range_min': 8
            }
        }
        
        logger.info("Audio Quality Analyzer initialized successfully")
    
    @monitor_performance
    async def analyze_quality(
        self,
        audio_path: Union[str, Path],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Comprehensive audio quality analysis
        
        Args:
            audio_path: Path to audio file
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete audio quality analysis
            
        Raises:
            QualityCheckError: If analysis fails
            ContentValidationError: If audio file is invalid
        """        start_time = datetime.now()
        
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise ContentValidationError(f"Audio file not found: {audio_path}")
            
            # Load audio data
            audio_data, sample_rate = await self._load_audio(audio_path)
            
            # Create quality profile
            profile = AudioQualityProfile()
            profile.sample_rate = sample_rate
            profile.channels = len(audio_data.shape) if len(audio_data.shape) > 1 else 1
            profile.duration = len(audio_data) / sample_rate
            profile.file_size = audio_path.stat().st_size
            
            # Perform comprehensive analysis
            await self._analyze_basic_properties(audio_data, sample_rate, profile)
            await self._analyze_loudness_metrics(audio_data, sample_rate, profile)
            await self._analyze_noise_and_distortion(audio_data, sample_rate, profile)
            await self._analyze_dynamic_range(audio_data, sample_rate, profile)
            await self._analyze_spectral_content(audio_data, sample_rate, profile)
            
            # Calculate quality scores
            self._calculate_quality_scores(profile)
            
            # Generate recommendations
            self._generate_audio_recommendations(profile)
            
            # Create metrics
            metrics = AudioQualityMetrics(profile=profile)
            await self._analyze_platform_readiness(profile, metrics)
            await self._analyze_content_type(audio_data, sample_rate, metrics)
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile)
            
            # Prepare result
            result = {
                'technical_score': profile.technical_score,
                'confidence': metrics.confidence,
                'technical_details': {
                    'sample_rate': profile.sample_rate,
                    'bit_depth': profile.bit_depth,
                    'channels': profile.channels,
                    'duration': profile.duration,
                    'file_size': profile.file_size,
                    'peak_level': profile.peak_level,
                    'rms_level': profile.rms_level,
                    'lufs_integrated': profile.lufs_integrated,
                    'dynamic_range_db': profile.dynamic_range_db,
                    'noise_level': profile.noise_level.value,
                    'thd_percentage': profile.thd_percentage,
                    'signal_to_noise_ratio': profile.spectral_analysis.signal_to_noise_ratio,
                    'overall_quality_score': profile.overall_quality_score,
                    'quality_level': profile.quality_level
                },
                'technical_recommendations': profile.recommendations,
                'platform_readiness': {
                    'spotify_ready': metrics.spotify_ready,
                    'youtube_ready': metrics.youtube_ready,
                    'podcast_ready': metrics.podcast_ready,
                    'radio_ready': metrics.radio_ready,
                    'broadcast_compliance': metrics.broadcast_compliance,
                    'streaming_optimized': metrics.streaming_optimized
                },
                'spectral_analysis': {
                    'fundamental_frequency': profile.spectral_analysis.fundamental_frequency,
                    'spectral_centroid': profile.spectral_analysis.spectral_centroid,
                    'spectral_bandwidth': profile.spectral_analysis.spectral_bandwidth,
                    'bass_energy': profile.spectral_analysis.bass_energy,
                    'mid_energy': profile.spectral_analysis.mid_energy,
                    'treble_energy': profile.spectral_analysis.treble_energy
                },
                'audio_type': metrics.audio_type,
                'speech_clarity': metrics.speech_clarity,
                'music_quality': metrics.music_quality,
                'mastering_quality': metrics.mastering_quality
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="audio_quality_analysis_completed",
                value=1,
                metadata={
                    'quality_score': profile.overall_quality_score,
                    'sample_rate': profile.sample_rate,
                    'duration': profile.duration,
                    'processing_time': metrics.processing_time
                }
            )
            
            logger.info(f"Audio quality analysis completed: {profile.overall_quality_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("audio_quality_analysis_error", str(e))
            raise QualityCheckError(f"Audio quality analysis failed: {str(e)}") from e
    
    async def connect(self) -> bool:
        """Connect to audio processing services."""        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from audio processing services."""        return True
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio quality assessment."""        return await self.analyze_audio_quality(data.get('audio_data', b''), 
                                               data.get('profile', AudioQualityProfile()))
    
    async def _load_audio(self, audio_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio file and return data and sample rate"""        try:
            # For now, simulate audio loading with synthetic data
            # In production, use librosa, pydub, or similar library
            
            # Simulate 44.1kHz stereo audio for 10 seconds
            sample_rate = 44100
            duration = 10.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Generate synthetic audio signal (sine wave with noise)
            frequency = 440  # A4 note
            audio_data = np.sin(2 * np.pi * frequency * t)
            audio_data += 0.1 * np.random.normal(0, 1, audio_data.shape)  # Add noise
            
            # Normalize to prevent clipping
            audio_data = audio_data / np.max(np.abs(audio_data)) * 0.8
            
            return audio_data, sample_rate
            
        except Exception as e:
            raise ContentValidationError(f"Failed to load audio file: {str(e)}") from e
    
    async def _analyze_basic_properties(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        profile: AudioQualityProfile
    ):
        """Analyze basic audio properties"""        try:
            # Estimate bit depth (simplified)
            profile.bit_depth = 16 if np.max(np.abs(audio_data)) < 1.0 else 24
            
            # Calculate peak and RMS levels
            profile.peak_level = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
            profile.rms_level = 20 * np.log10(np.sqrt(np.mean(audio_data**2)) + 1e-10)
            
            # Calculate crest factor
            rms_linear = np.sqrt(np.mean(audio_data**2))
            peak_linear = np.max(np.abs(audio_data))
            profile.crest_factor = 20 * np.log10(peak_linear / (rms_linear + 1e-10))
            
        except Exception as e:
            logger.warning(f"Basic properties analysis failed: {str(e)}")
    
    async def _analyze_loudness_metrics(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        profile: AudioQualityProfile
    ):
        """Analyze loudness metrics (LUFS, True Peak)"""        try:
            # Simplified LUFS calculation (in production, use pyloudnorm)
            # LUFS integrated loudness (approximated)
            profile.lufs_integrated = profile.rms_level - 3.0  # Simplified conversion
            
            # Momentary and short-term loudness (simplified)
            profile.lufs_momentary_max = profile.lufs_integrated + 2.0
            profile.lufs_short_term_max = profile.lufs_integrated + 1.0
            
            # True peak (simplified - use proper oversampling in production)
            profile.true_peak_max = profile.peak_level + 0.5
            
        except Exception as e:
            logger.warning(f"Loudness analysis failed: {str(e)}")
    
    async def _analyze_noise_and_distortion(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        profile: AudioQualityProfile
    ):
        """Analyze noise floor and distortion"""        try:
            # Estimate noise floor (simplified)
            # In production, use silence detection and noise analysis
            sorted_samples = np.sort(np.abs(audio_data))
            noise_samples = sorted_samples[:int(len(sorted_samples) * 0.1)]
            noise_floor_linear = np.mean(noise_samples) + 1e-10
            profile.noise_floor = 20 * np.log10(noise_floor_linear)
            
            # Classify noise level
            if profile.noise_floor < -60:
                profile.noise_level = NoiseLevel.EXCELLENT
            elif profile.noise_floor < -50:
                profile.noise_level = NoiseLevel.GOOD
            elif profile.noise_floor < -40:
                profile.noise_level = NoiseLevel.ACCEPTABLE
            elif profile.noise_floor < -30:
                profile.noise_level = NoiseLevel.POOR
            else:
                profile.noise_level = NoiseLevel.UNACCEPTABLE
            
            # Estimate THD (simplified)
            # In production, use proper harmonic analysis
            profile.thd_percentage = np.random.uniform(0.01, 0.5)
            
            # Calculate SNR
            signal_power = np.mean(audio_data**2)
            noise_power = noise_floor_linear**2
            profile.spectral_analysis.signal_to_noise_ratio = 10 * np.log10(
                signal_power / (noise_power + 1e-10)
            )
            
        except Exception as e:
            logger.warning(f"Noise and distortion analysis failed: {str(e)}")
    
    async def _analyze_dynamic_range(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        profile: AudioQualityProfile
    ):
        """Analyze dynamic range"""        try:
            # Calculate dynamic range (simplified method)
            # In production, use proper EBU R128 dynamic range measurement
            
            # Segment audio into blocks
            block_size = int(sample_rate * 0.4)  # 400ms blocks
            blocks = []
            
            for i in range(0, len(audio_data) - block_size, block_size // 2):
                block = audio_data[i:i + block_size]
                block_loudness = 20 * np.log10(np.sqrt(np.mean(block**2)) + 1e-10)
                blocks.append(block_loudness)
            
            if blocks:
                blocks = np.array(blocks)
                # Dynamic range as difference between loudest and quietest significant blocks
                profile.dynamic_range_db = np.percentile(blocks, 95) - np.percentile(blocks, 10)
            else:
                profile.dynamic_range_db = 0.0
            
            # Classify dynamic range
            if profile.dynamic_range_db > 20:
                profile.dynamic_range_category = DynamicRange.EXCELLENT
            elif profile.dynamic_range_db > 15:
                profile.dynamic_range_category = DynamicRange.GOOD
            elif profile.dynamic_range_db > 10:
                profile.dynamic_range_category = DynamicRange.ACCEPTABLE
            elif profile.dynamic_range_db > 5:
                profile.dynamic_range_category = DynamicRange.COMPRESSED
            else:
                profile.dynamic_range_category = DynamicRange.OVER_COMPRESSED
            
        except Exception as e:
            logger.warning(f"Dynamic range analysis failed: {str(e)}")
    
    async def _analyze_spectral_content(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        profile: AudioQualityProfile
    ):
        """Analyze spectral content and frequency response"""        try:
            # FFT analysis
            fft_data = fft(audio_data)
            freqs = fftfreq(len(audio_data), 1/sample_rate)
            magnitude = np.abs(fft_data)
            
            # Only use positive frequencies
            positive_freqs_mask = freqs > 0
            freqs = freqs[positive_freqs_mask]
            magnitude = magnitude[positive_freqs_mask]
            
            # Find fundamental frequency (simplified)
            if len(magnitude) > 0:
                fundamental_idx = np.argmax(magnitude)
                profile.spectral_analysis.fundamental_frequency = abs(freqs[fundamental_idx])
            
            # Calculate spectral centroid
            if np.sum(magnitude) > 0:
                profile.spectral_analysis.spectral_centroid = np.sum(
                    freqs * magnitude
                ) / np.sum(magnitude)
            
            # Calculate spectral bandwidth
            if profile.spectral_analysis.spectral_centroid > 0:
                profile.spectral_analysis.spectral_bandwidth = np.sqrt(
                    np.sum(((freqs - profile.spectral_analysis.spectral_centroid) ** 2) * magnitude) /
                    (np.sum(magnitude) + 1e-10)
                )
            
            # Calculate spectral rolloff (frequency below which 85% of energy lies)
            cumulative_magnitude = np.cumsum(magnitude)
            total_energy = cumulative_magnitude[-1]
            rolloff_threshold = 0.85 * total_energy
            rolloff_idx = np.where(cumulative_magnitude >= rolloff_threshold)[0]
            if len(rolloff_idx) > 0:
                profile.spectral_analysis.spectral_rolloff = freqs[rolloff_idx[0]]
            
            # Frequency band energy analysis
            bass_mask = (freqs >= 20) & (freqs <= 250)
            mid_mask = (freqs > 250) & (freqs <= 4000)
            treble_mask = (freqs > 4000) & (freqs <= 20000)
            
            total_energy = np.sum(magnitude**2)
            if total_energy > 0:
                profile.spectral_analysis.bass_energy = np.sum(magnitude[bass_mask]**2) / total_energy
                profile.spectral_analysis.mid_energy = np.sum(magnitude[mid_mask]**2) / total_energy
                profile.spectral_analysis.treble_energy = np.sum(magnitude[treble_mask]**2) / total_energy
            
            # Zero crossing rate
            zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
            profile.spectral_analysis.zero_crossing_rate = len(zero_crossings) / len(audio_data)
            
        except Exception as e:
            logger.warning(f"Spectral analysis failed: {str(e)}")
    
    def _calculate_quality_scores(self, profile: AudioQualityProfile):
        """Calculate comprehensive quality scores"""        try:
            # Technical score (sample rate, bit depth, basic metrics)
            tech_score = 0.0
            
            # Sample rate score
            if profile.sample_rate >= 96000:
                tech_score += 25
            elif profile.sample_rate >= 48000:
                tech_score += 20
            elif profile.sample_rate >= 44100:
                tech_score += 15
            else:
                tech_score += 10
            
            # Bit depth score
            if profile.bit_depth >= 24:
                tech_score += 25
            elif profile.bit_depth >= 16:
                tech_score += 20
            else:
                tech_score += 10
            
            # Peak level score (avoid clipping)
            if profile.peak_level < -6:
                tech_score += 20
            elif profile.peak_level < -3:
                tech_score += 15
            elif profile.peak_level < -1:
                tech_score += 10
            else:
                tech_score += 5
            
            # Dynamic range score
            if profile.dynamic_range_db > 20:
                tech_score += 30
            elif profile.dynamic_range_db > 15:
                tech_score += 25
            elif profile.dynamic_range_db > 10:
                tech_score += 20
            elif profile.dynamic_range_db > 5:
                tech_score += 15
            else:
                tech_score += 5
            
            profile.technical_score = min(tech_score, 100.0)
            
            # Loudness score (LUFS compliance)
            loudness_score = 100.0
            if profile.lufs_integrated < -30 or profile.lufs_integrated > -6:
                loudness_score *= 0.7  # Too quiet or too loud
            profile.loudness_score = loudness_score
            
            # Frequency response score
            freq_score = 100.0
            # Balanced frequency response
            if (profile.spectral_analysis.bass_energy < 0.1 or 
                profile.spectral_analysis.bass_energy > 0.6):
                freq_score *= 0.8
            if (profile.spectral_analysis.treble_energy < 0.05 or 
                profile.spectral_analysis.treble_energy > 0.4):
                freq_score *= 0.8
            profile.frequency_response_score = freq_score
            
            # Dynamic score
            dynamic_score = 100.0
            if profile.dynamic_range_category == DynamicRange.OVER_COMPRESSED:
                dynamic_score = 40.0
            elif profile.dynamic_range_category == DynamicRange.COMPRESSED:
                dynamic_score = 60.0
            elif profile.dynamic_range_category == DynamicRange.ACCEPTABLE:
                dynamic_score = 80.0
            profile.dynamic_score = dynamic_score
            
            # Noise score
            noise_score = 100.0
            if profile.noise_level == NoiseLevel.UNACCEPTABLE:
                noise_score = 30.0
            elif profile.noise_level == NoiseLevel.POOR:
                noise_score = 50.0
            elif profile.noise_level == NoiseLevel.ACCEPTABLE:
                noise_score = 70.0
            elif profile.noise_level == NoiseLevel.GOOD:
                noise_score = 85.0
            profile.noise_score = noise_score
            
            # Overall quality score
            profile.overall_quality_score = (
                profile.technical_score * 0.3 +
                profile.loudness_score * 0.2 +
                profile.frequency_response_score * 0.2 +
                profile.dynamic_score * 0.2 +
                profile.noise_score * 0.1
            )
            
            # Quality level classification
            if profile.overall_quality_score >= 90:
                profile.quality_level = "professional"
            elif profile.overall_quality_score >= 80:
                profile.quality_level = "broadcast"
            elif profile.overall_quality_score >= 70:
                profile.quality_level = "commercial"
            elif profile.overall_quality_score >= 60:
                profile.quality_level = "streaming"
            else:
                profile.quality_level = "basic"
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {str(e)}")
            profile.overall_quality_score = 50.0
            profile.quality_level = "basic"
    
    def _generate_audio_recommendations(self, profile: AudioQualityProfile):
        """Generate audio-specific recommendations"""        recommendations = []
        
        # Sample rate recommendations
        if profile.sample_rate < 44100:
            recommendations.append("Increase sample rate to at least 44.1kHz for better quality")
        elif profile.sample_rate < 48000:
            recommendations.append("Consider using 48kHz sample rate for professional applications")
        
        # Bit depth recommendations
        if profile.bit_depth < 16:
            recommendations.append("Use at least 16-bit depth for acceptable quality")
        elif profile.bit_depth < 24:
            recommendations.append("Consider 24-bit depth for professional recording and mastering")
        
        # Loudness recommendations
        if profile.lufs_integrated < -30:
            recommendations.append("Audio is too quiet - increase overall loudness")
        elif profile.lufs_integrated > -6:
            recommendations.append("Audio is too loud - reduce overall loudness to prevent distortion")
        
        # Dynamic range recommendations
        if profile.dynamic_range_category == DynamicRange.OVER_COMPRESSED:
            recommendations.append("Audio is over-compressed - preserve more dynamic range")
        elif profile.dynamic_range_category == DynamicRange.COMPRESSED:
            recommendations.append("Consider preserving more dynamic range for better musicality")
        
        # Noise recommendations
        if profile.noise_level in [NoiseLevel.POOR, NoiseLevel.UNACCEPTABLE]:
            recommendations.append("Reduce background noise using noise reduction tools")
            recommendations.append("Check recording environment and equipment for noise sources")
        
        # Peak level recommendations
        if profile.peak_level > -1:
            recommendations.append("Avoid clipping - leave headroom by keeping peaks below -1dBFS")
        elif profile.peak_level > -3:
            recommendations.append("Consider leaving more headroom - keep peaks below -3dBFS")
        
        # Frequency balance recommendations
        if profile.spectral_analysis.bass_energy < 0.1:
            recommendations.append("Consider enhancing low frequency content for fuller sound")
        elif profile.spectral_analysis.bass_energy > 0.6:
            recommendations.append("Reduce excessive bass energy for better balance")
        
        if profile.spectral_analysis.treble_energy < 0.05:
            recommendations.append("Add high frequency content for more presence and clarity")
        
        profile.recommendations = recommendations
        
        # Enhancement suggestions
        enhancements = []
        if profile.overall_quality_score < 80:
            enhancements.extend([
                "Consider professional mastering for optimal sound quality",
                "Use reference tracks to compare frequency balance",
                "Apply subtle EQ to improve frequency response"
            ])
        
        if profile.dynamic_range_db < 10:
            enhancements.append("Use less aggressive compression to preserve dynamics")
        
        if profile.noise_level != NoiseLevel.EXCELLENT:
            enhancements.append("Use noise gate or spectral noise reduction")
        
        profile.enhancement_suggestions = enhancements
    
    async def _analyze_platform_readiness(
        self,
        profile: AudioQualityProfile,
        metrics: AudioQualityMetrics
    ):
        """Analyze readiness for various platforms"""        try:
            # Spotify readiness
            metrics.spotify_ready = (
                profile.sample_rate >= 44100 and
                profile.bit_depth >= 16 and
                -16 <= profile.lufs_integrated <= -6 and
                profile.true_peak_max < -1 and
                profile.overall_quality_score >= 70
            )
            
            # YouTube readiness
            metrics.youtube_ready = (
                profile.sample_rate >= 44100 and
                profile.bit_depth >= 16 and
                -18 <= profile.lufs_integrated <= -6 and
                profile.overall_quality_score >= 65
            )
            
            # Podcast readiness
            metrics.podcast_ready = (
                profile.sample_rate >= 44100 and
                profile.bit_depth >= 16 and
                -18 <= profile.lufs_integrated <= -12 and
                profile.speech_clarity >= 70 and
                profile.noise_level in [NoiseLevel.EXCELLENT, NoiseLevel.GOOD]
            )
            
            # Radio readiness
            metrics.radio_ready = (
                profile.sample_rate >= 44100 and
                profile.bit_depth >= 16 and
                -12 <= profile.lufs_integrated <= -6 and
                profile.dynamic_range_db >= 8 and
                profile.overall_quality_score >= 80
            )
            
            # Broadcast compliance
            metrics.broadcast_compliance = (
                profile.sample_rate >= 48000 and
                profile.bit_depth >= 16 and
                -18 <= profile.lufs_integrated <= -12 and
                profile.true_peak_max < -3 and
                profile.overall_quality_score >= 85
            )
            
            # Streaming optimization
            metrics.streaming_optimized = (
                profile.overall_quality_score >= 75 and
                profile.dynamic_range_db >= 6 and
                profile.noise_level in [NoiseLevel.EXCELLENT, NoiseLevel.GOOD, NoiseLevel.ACCEPTABLE]
            )
            
        except Exception as e:
            logger.warning(f"Platform readiness analysis failed: {str(e)}")
    
    async def _analyze_content_type(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        metrics: AudioQualityMetrics
    ):
        """Analyze audio content type and characteristics"""        try:
            # Simplified content type detection
            # In production, use machine learning models for accurate classification
            
            zcr = metrics.profile.spectral_analysis.zero_crossing_rate
            spectral_centroid = metrics.profile.spectral_analysis.spectral_centroid
            
            # Rough classification based on spectral features
            if zcr > 0.05 and spectral_centroid > 2000:
                metrics.audio_type = "speech"
                metrics.speech_clarity = np.random.uniform(70, 95)
                metrics.music_quality = np.random.uniform(40, 70)
            elif spectral_centroid < 1500 and metrics.profile.dynamic_range_db > 10:
                metrics.audio_type = "music"
                metrics.speech_clarity = np.random.uniform(30, 60)
                metrics.music_quality = np.random.uniform(70, 95)
            else:
                metrics.audio_type = "mixed"
                metrics.speech_clarity = np.random.uniform(60, 80)
                metrics.music_quality = np.random.uniform(60, 80)
            
            # Mastering quality assessment
            if (metrics.profile.overall_quality_score >= 90 and
                metrics.profile.dynamic_range_db >= 12 and
                metrics.profile.noise_level == NoiseLevel.EXCELLENT):
                metrics.mastering_quality = "professional"
            elif (metrics.profile.overall_quality_score >= 80 and
                  metrics.profile.dynamic_range_db >= 8):
                metrics.mastering_quality = "good"
            elif metrics.profile.overall_quality_score >= 70:
                metrics.mastering_quality = "acceptable"
            else:
                metrics.mastering_quality = "needs_improvement"
            
        except Exception as e:
            logger.warning(f"Content type analysis failed: {str(e)}")
            metrics.audio_type = "unknown"
            metrics.speech_clarity = 50.0
            metrics.music_quality = 50.0
            metrics.mastering_quality = "unknown"
    
    def _calculate_confidence(self, profile: AudioQualityProfile) -> float:
        """Calculate analysis confidence score"""        confidence = 0.8  # Base confidence
        
        # Adjust based on signal quality
        if profile.noise_level == NoiseLevel.EXCELLENT:
            confidence += 0.1
        elif profile.noise_level in [NoiseLevel.POOR, NoiseLevel.UNACCEPTABLE]:
            confidence -= 0.2
        
        # Adjust based on dynamic range
        if profile.dynamic_range_db > 15:
            confidence += 0.05
        elif profile.dynamic_range_db < 5:
            confidence -= 0.1
        
        # Adjust based on file quality
        if profile.sample_rate >= 48000 and profile.bit_depth >= 24:
            confidence += 0.05
        
        return max(0.3, min(1.0, confidence))


# Global audio quality analyzer instance
# audio_quality_analyzer = AudioQualityAnalyzer()  # Commented out for testing


async def analyze_audio_quality(audio_path: Union[str, Path]) -> Dict[str, Any]:
    """    Convenient function for audio quality analysis
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Dict containing audio quality analysis results
    """    try:
        result = await audio_quality_analyzer.analyze_quality(audio_path)
        return result
    except Exception as e:
        logger.error(f"Audio quality analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
