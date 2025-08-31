"""Audio Quality Analyzer & Metrics Engine
=======================================

Professional audio quality analysis system providing comprehensive metrics,
quality assessment, and enhancement validation for content creators.
Supports psychoacoustic evaluation, spectral analysis, and perceptual quality metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""
import numpy as np
import librosa
import scipy.signal as signal
from scipy.stats import entropy, kurtosis, skew
from scipy.fft import fft, fftfreq
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import json
import time
import warnings

from ..core.exceptions import AudioProcessingError
from ..core.validators import AudioValidator


class QualityLevel(Enum):
    """Audio quality assessment levels"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 75-89%
    FAIR = "fair"             # 60-74%
    POOR = "poor"             # 40-59%
    BAD = "bad"               # 0-39%


class MetricCategory(Enum):
    """Audio quality metric categories"""
    TEMPORAL = "temporal"          # Time-domain metrics
    SPECTRAL = "spectral"          # Frequency-domain metrics
    PSYCHOACOUSTIC = "psychoacoustic"  # Perceptual metrics
    DISTORTION = "distortion"      # Distortion measurements
    DYNAMIC = "dynamic"            # Dynamic range metrics
    SPATIAL = "spatial"            # Stereo/surround metrics


@dataclass
class QualityMetrics:
    """Comprehensive audio quality metrics"""
    # Basic metrics
    peak_amplitude: float = 0.0
    rms_level: float = 0.0
    rms_db: float = -np.inf
    crest_factor: float = 0.0
    
    # Dynamic range metrics
    dynamic_range_db: float = 0.0
    loudness_lufs: float = -np.inf
    loudness_range_lu: float = 0.0
    true_peak_dbfs: float = -np.inf
    
    # Spectral metrics
    spectral_centroid: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_rolloff: float = 0.0
    spectral_flatness: float = 0.0
    spectral_flux: float = 0.0
    
    # Harmonic metrics
    fundamental_frequency: float = 0.0
    harmonic_ratio: float = 0.0
    inharmonicity: float = 0.0
    
    # Noise metrics
    snr_db: float = 0.0
    thd_percent: float = 0.0
    thdn_percent: float = 0.0
    
    # Psychoacoustic metrics
    perceived_loudness: float = 0.0
    sharpness: float = 0.0
    roughness: float = 0.0
    fluctuation_strength: float = 0.0
    
    # Temporal metrics
    zero_crossing_rate: float = 0.0
    tempo_bpm: float = 0.0
    onset_density: float = 0.0
    
    # Distortion metrics
    clipping_factor: float = 0.0
    dc_offset: float = 0.0
    inter_channel_correlation: float = 0.0
    
    # Quality scores
    overall_quality_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.FAIR
    
    # Metadata
    analysis_timestamp: float = field(default_factory=time.time)
    sample_rate: int = 0
    duration_seconds: float = 0.0
    channels: int = 0


@dataclass
class ComparisonResult:
    """Audio quality comparison results"""
    reference_metrics: QualityMetrics
    test_metrics: QualityMetrics
    improvement_scores: Dict[str, float] = field(default_factory=dict)
    degradation_scores: Dict[str, float] = field(default_factory=dict)
    overall_improvement: float = 0.0
    recommendation: str = ""
    warnings: List[str] = field(default_factory=list)


class PsychoacousticAnalyzer:
    """Advanced psychoacoustic analysis based on human auditory perception"""
    
    def __init__(self):
        self.bark_scale_boundaries = self._create_bark_scale()
        self.a_weighting_filter = self._create_a_weighting_filter()
    
    def _create_bark_scale(self) -> np.ndarray:
        """Create Bark scale frequency boundaries"""
        # Bark scale critical bands (Hz)
        return np.array([
            20, 100, 200, 300, 400, 510, 630, 770, 920, 1080,
            1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400,
            5300, 6400, 7700, 9500, 12000, 15500, 20000
        ])
    
    def _create_a_weighting_filter(self) -> Dict[str, np.ndarray]:
        """Create A-weighting filter coefficients"""
        # Simplified A-weighting approximation
        freqs = np.logspace(np.log10(20), np.log10(20000), 1000)
        
        # A-weighting formula
        f = freqs
        f2 = f ** 2
        c1 = 12200 ** 2
        c2 = 20.6 ** 2
        c3 = 107.7 ** 2
        c4 = 737.9 ** 2
        
        numerator = c1 * f2 * f2
        denominator = (f2 + c2) * np.sqrt((f2 + c3) * (f2 + c4)) * (f2 + c1)
        
        a_weighting_linear = numerator / denominator
        a_weighting_db = 20 * np.log10(a_weighting_linear)
        
        # Normalize to 0 dB at 1 kHz
        normalization = -a_weighting_db[np.argmin(np.abs(freqs - 1000))]
        a_weighting_db += normalization
        
        return {
            'frequencies': freqs,
            'weights_db': a_weighting_db
        }
    
    def analyze_loudness(self, audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze perceptual loudness using ITU-R BS.1770 standard"""
        # Pre-filter (high-pass)
        sos = signal.butter(2, 48, btype='high', fs=sample_rate, output='sos')
        filtered_audio = signal.sosfilt(sos, audio, axis=0)
        
        # RLB weighting filter (for stereo)
        if len(filtered_audio.shape) > 1 and filtered_audio.shape[1] >= 2:
            # Apply channel weighting
            left_weight = 1.0
            right_weight = 1.0
            weighted_sum = (left_weight * filtered_audio[:, 0] ** 2 + 
                           right_weight * filtered_audio[:, 1] ** 2)
        else:
            weighted_sum = filtered_audio.flatten() ** 2
        
        # Gating
        block_size = int(0.4 * sample_rate)  # 400ms blocks
        hop_size = int(0.1 * sample_rate)    # 100ms overlap
        
        loudness_blocks = []
        for i in range(0, len(weighted_sum) - block_size + 1, hop_size):
            block = weighted_sum[i:i + block_size]
            block_loudness = -0.691 + 10 * np.log10(np.mean(block) + 1e-10)
            loudness_blocks.append(block_loudness)
        
        if not loudness_blocks:
            return {
                'momentary_lufs': -np.inf,
                'integrated_lufs': -np.inf,
                'loudness_range': 0.0,
                'true_peak_dbfs': 20 * np.log10(np.max(np.abs(audio)) + 1e-10)
            }
        
        loudness_blocks = np.array(loudness_blocks)
        
        # Absolute gating (-70 LUFS)
        gated_blocks = loudness_blocks[loudness_blocks > -70]
        
        if len(gated_blocks) == 0:
            integrated_loudness = -np.inf
        else:
            # Relative gating
            relative_threshold = np.mean(gated_blocks) - 10
            relative_gated = gated_blocks[gated_blocks > relative_threshold]
            
            if len(relative_gated) == 0:
                integrated_loudness = -np.inf
            else:
                integrated_loudness = np.mean(relative_gated)
        
        # Loudness range
        if len(gated_blocks) > 0:
            loudness_range = np.percentile(gated_blocks, 95) - np.percentile(gated_blocks, 10)
        else:
            loudness_range = 0.0
        
        # True peak
        upsampled_audio = signal.resample(audio, len(audio) * 4, axis=0)
        true_peak_dbfs = 20 * np.log10(np.max(np.abs(upsampled_audio)) + 1e-10)
        
        return {
            'momentary_lufs': loudness_blocks[-1] if loudness_blocks.size > 0 else -np.inf,
            'integrated_lufs': integrated_loudness,
            'loudness_range': loudness_range,
            'true_peak_dbfs': true_peak_dbfs
        }
    
    def calculate_sharpness(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate perceptual sharpness (Zwicker and Fastl)"""
        # FFT analysis
        n_fft = 2048
        hop_length = n_fft // 4
        
        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # Convert to Bark scale
        freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
        bark_values = 13 * np.arctan(0.00076 * freqs) + 3.5 * np.arctan((freqs / 7500) ** 2)
        
        # Calculate specific loudness in each Bark band
        sharpness_values = []
        for frame in range(magnitude.shape[1]):
            frame_magnitude = magnitude[:, frame]
            
            # Weight by sharpness weighting function
            sharpness_weight = 0.11 * bark_values + 0.1
            weighted_magnitude = frame_magnitude * sharpness_weight
            
            # Calculate sharpness
            total_loudness = np.sum(frame_magnitude)
            if total_loudness > 0:
                sharpness = np.sum(weighted_magnitude) / total_loudness
            else:
                sharpness = 0.0
            
            sharpness_values.append(sharpness)
        
        return np.mean(sharpness_values)
    
    def calculate_roughness(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate perceptual roughness"""
        # Analyze modulation in critical bands
        n_fft = 2048
        hop_length = n_fft // 8  # High temporal resolution
        
        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        roughness_sum = 0.0
        band_count = 0
        
        # Process each critical band
        for i in range(len(self.bark_scale_boundaries) - 1):
            low_freq = self.bark_scale_boundaries[i]
            high_freq = self.bark_scale_boundaries[i + 1]
            
            # Find frequency bins for this band
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
            band_mask = (freqs >= low_freq) & (freqs < high_freq)
            
            if not np.any(band_mask):
                continue
            
            # Extract band magnitude over time
            band_magnitude = np.sum(magnitude[band_mask, :], axis=0)
            
            if len(band_magnitude) < 2:
                continue
            
            # Calculate modulation spectrum
            mod_spectrum = np.abs(fft(band_magnitude - np.mean(band_magnitude)))
            mod_freqs = fftfreq(len(band_magnitude), d=hop_length/sample_rate)
            
            # Focus on modulation frequencies that cause roughness (15-300 Hz)
            mod_mask = (np.abs(mod_freqs) >= 15) & (np.abs(mod_freqs) <= 300)
            if np.any(mod_mask):
                band_roughness = np.sum(mod_spectrum[mod_mask])
                roughness_sum += band_roughness
                band_count += 1
        
        return roughness_sum / max(band_count, 1)


class AudioQualityAnalyzer:
    """
    Professional Audio Quality Analyzer & Metrics Engine
    
    Comprehensive audio quality analysis system providing detailed metrics,
    quality assessment, and enhancement validation capabilities.
    """
    
    def __init__(self):
        """Initialize the audio quality analyzer"""
        self.logger = logging.getLogger(__name__)
        self.validator = AudioValidator()
        self.psychoacoustic_analyzer = PsychoacousticAnalyzer()
        
        # Quality thresholds configuration
        self.quality_thresholds = self._init_quality_thresholds()
        
        # Analysis cache
        self._analysis_cache = {}
        
    def _init_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize quality assessment thresholds"""
        return {
            'snr_db': {
                'excellent': 50.0,
                'good': 35.0,
                'fair': 25.0,
                'poor': 15.0
            },
            'thd_percent': {
                'excellent': 0.1,
                'good': 0.5,
                'fair': 1.0,
                'poor': 3.0
            },
            'dynamic_range_db': {
                'excellent': 20.0,
                'good': 15.0,
                'fair': 10.0,
                'poor': 6.0
            },
            'spectral_flatness': {
                'excellent': 0.5,
                'good': 0.3,
                'fair': 0.2,
                'poor': 0.1
            }
        }
    
    def analyze_quality(self, 
                       audio: np.ndarray, 
                       sample_rate: int,
                       detailed: bool = True) -> QualityMetrics:
        """
        Perform comprehensive audio quality analysis
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            detailed: Enable detailed psychoacoustic analysis
            
        Returns:
            QualityMetrics object with comprehensive analysis results
        """
        try:
            # Validate input
            self.validator.validate_audio_array(audio, sample_rate)
            
            # Initialize metrics
            metrics = QualityMetrics()
            metrics.sample_rate = sample_rate
            metrics.duration_seconds = len(audio) / sample_rate
            metrics.channels = 1 if len(audio.shape) == 1 else audio.shape[1]
            
            # Convert to mono for analysis if needed
            if len(audio.shape) > 1:
                audio_mono = np.mean(audio, axis=1)
            else:
                audio_mono = audio
            
            # Basic temporal metrics
            self._analyze_temporal_metrics(audio_mono, sample_rate, metrics)
            
            # Spectral analysis
            self._analyze_spectral_metrics(audio_mono, sample_rate, metrics)
            
            # Dynamic range analysis
            self._analyze_dynamic_metrics(audio_mono, sample_rate, metrics)
            
            # Harmonic analysis
            self._analyze_harmonic_metrics(audio_mono, sample_rate, metrics)
            
            # Distortion analysis
            self._analyze_distortion_metrics(audio_mono, sample_rate, metrics)
            
            # Noise analysis
            self._analyze_noise_metrics(audio_mono, sample_rate, metrics)
            
            # Stereo analysis (if applicable)
            if len(audio.shape) > 1:
                self._analyze_spatial_metrics(audio, sample_rate, metrics)
            
            # Psychoacoustic analysis (if detailed)
            if detailed:
                self._analyze_psychoacoustic_metrics(audio_mono, sample_rate, metrics)
            
            # Calculate overall quality score
            metrics.overall_quality_score = self._calculate_overall_quality(metrics)
            metrics.quality_level = self._determine_quality_level(metrics.overall_quality_score)
            
            self.logger.debug(f"Quality analysis completed: {metrics.quality_level.value} "
                            f"({metrics.overall_quality_score:.1f}%)")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {str(e)}")
            raise AudioProcessingError(f"Quality analysis failed: {str(e)}")
    
    def _analyze_temporal_metrics(self, audio: np.ndarray, sample_rate: int, 
                                 metrics: QualityMetrics):
        """Analyze time-domain characteristics"""
        # Basic amplitude metrics
        metrics.peak_amplitude = np.max(np.abs(audio))
        metrics.rms_level = np.sqrt(np.mean(audio ** 2))
        metrics.rms_db = 20 * np.log10(metrics.rms_level + 1e-10)
        
        # Crest factor
        if metrics.rms_level > 0:
            metrics.crest_factor = metrics.peak_amplitude / metrics.rms_level
        
        # Zero crossing rate
        zero_crossings = np.where(np.diff(np.signbit(audio)))[0]
        metrics.zero_crossing_rate = len(zero_crossings) / len(audio)
        
        # DC offset
        metrics.dc_offset = np.abs(np.mean(audio))
        
        # Clipping detection
        clipped_samples = np.sum(np.abs(audio) > 0.99)
        metrics.clipping_factor = clipped_samples / len(audio)
        
        # Onset detection for tempo/rhythm analysis
        try:
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sample_rate, 
                                                     units='frames')
            metrics.onset_density = len(onset_frames) / metrics.duration_seconds
            
            # Estimate tempo
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
            metrics.tempo_bpm = float(tempo) if np.isfinite(tempo) else 0.0
            
        except Exception:
            metrics.onset_density = 0.0
            metrics.tempo_bpm = 0.0
    
    def _analyze_spectral_metrics(self, audio: np.ndarray, sample_rate: int,
                                 metrics: QualityMetrics):
        """Analyze frequency-domain characteristics"""
        try:
            # Spectral features using librosa
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            metrics.spectral_centroid = np.mean(spectral_centroids)
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
            metrics.spectral_bandwidth = np.mean(spectral_bandwidth)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            metrics.spectral_rolloff = np.mean(spectral_rolloff)
            
            # Spectral flatness
            spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
            metrics.spectral_flatness = np.mean(spectral_flatness)
            
            # Spectral flux (measure of spectral change)
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            spectral_flux = np.mean(np.sum(np.diff(magnitude, axis=1) ** 2, axis=0))
            metrics.spectral_flux = spectral_flux
            
        except Exception as e:
            self.logger.warning(f"Spectral analysis warning: {str(e)}")
            # Set default values
            metrics.spectral_centroid = 0.0
            metrics.spectral_bandwidth = 0.0
            metrics.spectral_rolloff = 0.0
            metrics.spectral_flatness = 0.0
            metrics.spectral_flux = 0.0
    
    def _analyze_dynamic_metrics(self, audio: np.ndarray, sample_rate: int,
                                metrics: QualityMetrics):
        """Analyze dynamic range characteristics"""
        # Basic dynamic range
        peak_db = 20 * np.log10(metrics.peak_amplitude + 1e-10)
        metrics.dynamic_range_db = peak_db - metrics.rms_db
        
        # Psychoacoustic loudness analysis
        loudness_results = self.psychoacoustic_analyzer.analyze_loudness(audio, sample_rate)
        metrics.loudness_lufs = loudness_results['integrated_lufs']
        metrics.loudness_range_lu = loudness_results['loudness_range']
        metrics.true_peak_dbfs = loudness_results['true_peak_dbfs']
    
    def _analyze_harmonic_metrics(self, audio: np.ndarray, sample_rate: int,
                                 metrics: QualityMetrics):
        """Analyze harmonic content"""
        try:
            # Fundamental frequency detection
            f0, voiced_flag, voiced_probs = librosa.pyin(audio, 
                                                        fmin=librosa.note_to_hz('C2'), 
                                                        fmax=librosa.note_to_hz('C7'),
                                                        sr=sample_rate)
            
            # Average fundamental frequency
            valid_f0 = f0[np.isfinite(f0) & (voiced_probs > 0.5)]
            if len(valid_f0) > 0:
                metrics.fundamental_frequency = np.mean(valid_f0)
            
            # Harmonic-to-noise ratio estimation
            if len(valid_f0) > 0:
                # Simple harmonic ratio calculation
                stft = librosa.stft(audio)
                magnitude = np.abs(stft)
                freqs = librosa.fft_frequencies(sr=sample_rate)
                
                # Find harmonic peaks
                f0_mean = np.mean(valid_f0)
                harmonic_energy = 0.0
                total_energy = np.sum(magnitude ** 2)
                
                for harmonic in range(1, 6):  # First 5 harmonics
                    target_freq = f0_mean * harmonic
                    freq_idx = np.argmin(np.abs(freqs - target_freq))
                    if freq_idx < len(magnitude):
                        # Sum energy in a small band around the harmonic
                        start_idx = max(0, freq_idx - 2)
                        end_idx = min(len(magnitude), freq_idx + 3)
                        harmonic_energy += np.sum(magnitude[start_idx:end_idx] ** 2)
                
                if total_energy > 0:
                    metrics.harmonic_ratio = harmonic_energy / total_energy
                
        except Exception as e:
            self.logger.warning(f"Harmonic analysis warning: {str(e)}")
            metrics.fundamental_frequency = 0.0
            metrics.harmonic_ratio = 0.0
    
    def _analyze_distortion_metrics(self, audio: np.ndarray, sample_rate: int,
                                   metrics: QualityMetrics):
        """Analyze distortion characteristics"""
        # Total Harmonic Distortion (THD) estimation
        try:
            # FFT-based THD calculation
            n_fft = min(8192, len(audio))
            if n_fft < 512:
                metrics.thd_percent = 0.0
                metrics.thdn_percent = 0.0
                return
            
            # Window the signal
            windowed = audio[:n_fft] * np.hanning(n_fft)
            spectrum = np.fft.fft(windowed)
            magnitude = np.abs(spectrum[:n_fft // 2])
            freqs = np.fft.fftfreq(n_fft, 1/sample_rate)[:n_fft // 2]
            
            # Find fundamental frequency peak
            fundamental_idx = np.argmax(magnitude[10:len(magnitude)//8]) + 10
            fundamental_freq = freqs[fundamental_idx]
            fundamental_magnitude = magnitude[fundamental_idx]
            
            # Find harmonic peaks
            harmonic_magnitudes = []
            for harmonic in range(2, 6):  # 2nd to 5th harmonics
                target_freq = fundamental_freq * harmonic
                if target_freq > sample_rate / 2:
                    break
                
                # Find closest frequency bin
                harmonic_idx = np.argmin(np.abs(freqs - target_freq))
                if harmonic_idx < len(magnitude):
                    harmonic_magnitudes.append(magnitude[harmonic_idx])
            
            # Calculate THD
            if fundamental_magnitude > 0 and harmonic_magnitudes:
                harmonic_power = np.sum(np.array(harmonic_magnitudes) ** 2)
                fundamental_power = fundamental_magnitude ** 2
                metrics.thd_percent = 100 * np.sqrt(harmonic_power / fundamental_power)
            
            # THD+N (include noise floor)
            noise_floor = np.mean(magnitude[magnitude < np.max(magnitude) * 0.1])
            noise_power = noise_floor ** 2 * len(magnitude)
            if fundamental_power > 0:
                metrics.thdn_percent = 100 * np.sqrt((harmonic_power + noise_power) / fundamental_power)
            
        except Exception as e:
            self.logger.warning(f"Distortion analysis warning: {str(e)}")
            metrics.thd_percent = 0.0
            metrics.thdn_percent = 0.0
    
    def _analyze_noise_metrics(self, audio: np.ndarray, sample_rate: int,
                              metrics: QualityMetrics):
        """Analyze noise characteristics"""
        # Signal-to-noise ratio estimation
        try:
            # Simple energy-based SNR estimation
            # Find signal and noise portions based on amplitude
            threshold = np.percentile(np.abs(audio), 80)
            signal_samples = audio[np.abs(audio) > threshold]
            noise_samples = audio[np.abs(audio) <= threshold]
            
            if len(signal_samples) > 0 and len(noise_samples) > 0:
                signal_power = np.mean(signal_samples ** 2)
                noise_power = np.mean(noise_samples ** 2)
                
                if noise_power > 0:
                    metrics.snr_db = 10 * np.log10(signal_power / noise_power)
                else:
                    metrics.snr_db = 60.0  # Very clean signal
            else:
                metrics.snr_db = 0.0
                
        except Exception as e:
            self.logger.warning(f"Noise analysis warning: {str(e)}")
            metrics.snr_db = 0.0
    
    def _analyze_spatial_metrics(self, audio: np.ndarray, sample_rate: int,
                                metrics: QualityMetrics):
        """Analyze stereo/spatial characteristics"""
        if audio.shape[1] < 2:
            return
        
        # Inter-channel correlation
        left_channel = audio[:, 0]
        right_channel = audio[:, 1]
        
        correlation_matrix = np.corrcoef(left_channel, right_channel)
        metrics.inter_channel_correlation = correlation_matrix[0, 1]
    
    def _analyze_psychoacoustic_metrics(self, audio: np.ndarray, sample_rate: int,
                                       metrics: QualityMetrics):
        """Analyze psychoacoustic characteristics"""
        try:
            # Perceptual sharpness
            metrics.sharpness = self.psychoacoustic_analyzer.calculate_sharpness(audio, sample_rate)
            
            # Perceptual roughness
            metrics.roughness = self.psychoacoustic_analyzer.calculate_roughness(audio, sample_rate)
            
            # Perceived loudness (simplified)
            metrics.perceived_loudness = max(0.0, (metrics.rms_db + 90) / 90)
            
        except Exception as e:
            self.logger.warning(f"Psychoacoustic analysis warning: {str(e)}")
            metrics.sharpness = 0.0
            metrics.roughness = 0.0
            metrics.perceived_loudness = 0.0
    
    def _calculate_overall_quality(self, metrics: QualityMetrics) -> float:
        """Calculate overall quality score (0-100)"""
        score_components = []
        weights = []
        
        # SNR component (25% weight)
        if metrics.snr_db > 0:
            snr_score = min(100, max(0, (metrics.snr_db - 10) * 2))
            score_components.append(snr_score)
            weights.append(0.25)
        
        # Dynamic range component (20% weight)
        if metrics.dynamic_range_db > 0:
            dr_score = min(100, max(0, metrics.dynamic_range_db * 4))
            score_components.append(dr_score)
            weights.append(0.20)
        
        # THD component (20% weight)
        if metrics.thd_percent >= 0:
            thd_score = max(0, 100 - metrics.thd_percent * 10)
            score_components.append(thd_score)
            weights.append(0.20)
        
        # Spectral flatness component (15% weight)
        spectral_score = min(100, metrics.spectral_flatness * 200)
        score_components.append(spectral_score)
        weights.append(0.15)
        
        # Clipping penalty (10% weight)
        clipping_score = max(0, 100 - metrics.clipping_factor * 1000)
        score_components.append(clipping_score)
        weights.append(0.10)
        
        # Peak level component (10% weight)
        if metrics.peak_amplitude > 0:
            # Penalize both too low and too high levels
            optimal_peak = 0.7
            peak_deviation = abs(metrics.peak_amplitude - optimal_peak)
            peak_score = max(0, 100 - peak_deviation * 200)
            score_components.append(peak_score)
            weights.append(0.10)
        
        # Calculate weighted average
        if score_components:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(score_components, weights))
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 50.0  # Default neutral score
        
        return max(0.0, min(100.0, overall_score))
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on overall score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.FAIR
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.BAD
    
    def compare_quality(self, 
                       reference_audio: np.ndarray,
                       test_audio: np.ndarray,
                       sample_rate: int) -> ComparisonResult:
        """
        Compare quality between reference and test audio
        
        Args:
            reference_audio: Reference audio signal
            test_audio: Test audio signal to compare
            sample_rate: Sample rate in Hz
            
        Returns:
            ComparisonResult with detailed comparison analysis
        """
        try:
            # Analyze both audio signals
            ref_metrics = self.analyze_quality(reference_audio, sample_rate)
            test_metrics = self.analyze_quality(test_audio, sample_rate)
            
            # Calculate improvements and degradations
            improvement_scores = {}
            degradation_scores = {}
            
            # Compare key metrics
            metrics_to_compare = [
                'snr_db', 'thd_percent', 'dynamic_range_db', 'spectral_flatness',
                'clipping_factor', 'overall_quality_score'
            ]
            
            for metric_name in metrics_to_compare:
                ref_value = getattr(ref_metrics, metric_name)
                test_value = getattr(test_metrics, metric_name)
                
                if metric_name in ['thd_percent', 'clipping_factor']:
                    # Lower is better for these metrics
                    if ref_value > 0:
                        improvement = ((ref_value - test_value) / ref_value) * 100
                    else:
                        improvement = 0.0
                else:
                    # Higher is better for these metrics
                    if ref_value > 0:
                        improvement = ((test_value - ref_value) / ref_value) * 100
                    else:
                        improvement = test_value  # Absolute improvement if ref was zero
                
                if improvement > 0:
                    improvement_scores[metric_name] = improvement
                else:
                    degradation_scores[metric_name] = abs(improvement)
            
            # Calculate overall improvement
            overall_improvement = test_metrics.overall_quality_score - ref_metrics.overall_quality_score
            
            # Generate recommendation
            recommendation = self._generate_comparison_recommendation(
                improvement_scores, degradation_scores, overall_improvement
            )
            
            # Generate warnings
            warnings = self._generate_comparison_warnings(ref_metrics, test_metrics)
            
            result = ComparisonResult(
                reference_metrics=ref_metrics,
                test_metrics=test_metrics,
                improvement_scores=improvement_scores,
                degradation_scores=degradation_scores,
                overall_improvement=overall_improvement,
                recommendation=recommendation,
                warnings=warnings
            )
            
            self.logger.info(f"Quality comparison completed. Overall improvement: {overall_improvement:.1f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Quality comparison failed: {str(e)}")
            raise AudioProcessingError(f"Quality comparison failed: {str(e)}")
    
    def _generate_comparison_recommendation(self, 
                                          improvements: Dict[str, float],
                                          degradations: Dict[str, float],
                                          overall_improvement: float) -> str:
        """Generate quality comparison recommendation"""
        if overall_improvement > 10:
            return "Excellent improvement achieved. The enhanced audio shows significant quality gains."
        elif overall_improvement > 5:
            return "Good improvement. The enhanced audio quality is noticeably better."
        elif overall_improvement > 0:
            return "Modest improvement. Some quality gains are present but limited."
        elif overall_improvement > -5:
            return "Minimal change. Quality remains approximately the same."
        elif overall_improvement > -10:
            return "Minor degradation. Consider adjusting enhancement parameters."
        else:
            return "Significant degradation. Enhancement parameters need major adjustment."
    
    def _generate_comparison_warnings(self, 
                                    ref_metrics: QualityMetrics,
                                    test_metrics: QualityMetrics) -> List[str]:
        """Generate warnings for quality comparison"""
        warnings = []
        
        # Clipping warning
        if test_metrics.clipping_factor > ref_metrics.clipping_factor * 2:
            warnings.append("Significant increase in clipping detected")
        
        # Dynamic range warning
        if test_metrics.dynamic_range_db < ref_metrics.dynamic_range_db - 6:
            warnings.append("Substantial dynamic range reduction")
        
        # THD warning
        if test_metrics.thd_percent > ref_metrics.thd_percent * 2 and test_metrics.thd_percent > 1.0:
            warnings.append("Increased distortion levels detected")
        
        # Spectral changes warning
        spectral_change = abs(test_metrics.spectral_centroid - ref_metrics.spectral_centroid)
        if spectral_change > 2000:
            warnings.append("Large spectral characteristic changes")
        
        return warnings
    
    def export_metrics(self, metrics: QualityMetrics, file_path: Union[str, Path]):
        """Export quality metrics to JSON file"""
        metrics_dict = {
            'analysis_info': {
                'timestamp': metrics.analysis_timestamp,
                'sample_rate': metrics.sample_rate,
                'duration_seconds': metrics.duration_seconds,
                'channels': metrics.channels
            },
            'basic_metrics': {
                'peak_amplitude': metrics.peak_amplitude,
                'rms_level': metrics.rms_level,
                'rms_db': metrics.rms_db,
                'crest_factor': metrics.crest_factor
            },
            'dynamic_metrics': {
                'dynamic_range_db': metrics.dynamic_range_db,
                'loudness_lufs': metrics.loudness_lufs,
                'loudness_range_lu': metrics.loudness_range_lu,
                'true_peak_dbfs': metrics.true_peak_dbfs
            },
            'spectral_metrics': {
                'spectral_centroid': metrics.spectral_centroid,
                'spectral_bandwidth': metrics.spectral_bandwidth,
                'spectral_rolloff': metrics.spectral_rolloff,
                'spectral_flatness': metrics.spectral_flatness,
                'spectral_flux': metrics.spectral_flux
            },
            'harmonic_metrics': {
                'fundamental_frequency': metrics.fundamental_frequency,
                'harmonic_ratio': metrics.harmonic_ratio,
                'inharmonicity': metrics.inharmonicity
            },
            'noise_distortion_metrics': {
                'snr_db': metrics.snr_db,
                'thd_percent': metrics.thd_percent,
                'thdn_percent': metrics.thdn_percent,
                'clipping_factor': metrics.clipping_factor,
                'dc_offset': metrics.dc_offset
            },
            'psychoacoustic_metrics': {
                'perceived_loudness': metrics.perceived_loudness,
                'sharpness': metrics.sharpness,
                'roughness': metrics.roughness,
                'fluctuation_strength': metrics.fluctuation_strength
            },
            'temporal_metrics': {
                'zero_crossing_rate': metrics.zero_crossing_rate,
                'tempo_bpm': metrics.tempo_bpm,
                'onset_density': metrics.onset_density
            },
            'spatial_metrics': {
                'inter_channel_correlation': metrics.inter_channel_correlation
            },
            'quality_assessment': {
                'overall_quality_score': metrics.overall_quality_score,
                'quality_level': metrics.quality_level.value
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(metrics_dict, f, indent=2, default=str)
    
    def get_quality_report(self, metrics: QualityMetrics) -> str:
        """Generate human-readable quality report"""
        report = []
        report.append("=== AUDIO QUALITY ANALYSIS REPORT ===\n")
        
        # Basic info
        report.append(f"Duration: {metrics.duration_seconds:.2f} seconds")
        report.append(f"Sample Rate: {metrics.sample_rate} Hz")
        report.append(f"Channels: {metrics.channels}")
        report.append("")
        
        # Overall assessment
        report.append(f"Overall Quality: {metrics.quality_level.value.upper()}")
        report.append(f"Quality Score: {metrics.overall_quality_score:.1f}/100")
        report.append("")
        
        # Key metrics
        report.append("=== KEY METRICS ===")
        report.append(f"Peak Level: {20 * np.log10(metrics.peak_amplitude + 1e-10):.1f} dBFS")
        report.append(f"RMS Level: {metrics.rms_db:.1f} dBFS")
        report.append(f"Dynamic Range: {metrics.dynamic_range_db:.1f} dB")
        report.append(f"Signal-to-Noise Ratio: {metrics.snr_db:.1f} dB")
        report.append(f"Total Harmonic Distortion: {metrics.thd_percent:.2f}%")
        report.append("")
        
        # Warnings and recommendations
        warnings = []
        if metrics.clipping_factor > 0.001:
            warnings.append(f"Clipping detected ({metrics.clipping_factor*100:.2f}% of samples)")
        if metrics.dc_offset > 0.01:
            warnings.append("Significant DC offset present")
        if metrics.dynamic_range_db < 6:
            warnings.append("Very limited dynamic range")
        if metrics.thd_percent > 3.0:
            warnings.append("High distortion levels")
        
        if warnings:
            report.append("=== WARNINGS ===")
            for warning in warnings:
                report.append(f"⚠️  {warning}")
            report.append("")
        
        # Quality recommendations
        recommendations = []
        if metrics.overall_quality_score < 60:
            recommendations.append("Consider audio enhancement to improve quality")
        if metrics.dynamic_range_db < 10:
            recommendations.append("Dynamic range expansion may be beneficial")
        if metrics.snr_db < 25:
            recommendations.append("Noise reduction processing recommended")
        
        if recommendations:
            report.append("=== RECOMMENDATIONS ===")
            for rec in recommendations:
                report.append(f"💡 {rec}")
        
        return "\n".join(report)
