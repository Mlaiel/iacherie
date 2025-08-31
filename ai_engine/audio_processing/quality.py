"""🎯 Audio Quality Assessment - Professional Quality Analysis Engine

Advanced quality assessment system for comprehensive audio evaluation.
Includes perceptual quality metrics, technical analysis, and optimization recommendations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import numpy as np
import librosa
from scipy import signal, stats
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum
import tempfile
import warnings

from .core import AudioProcessor, AudioMetadata
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class QualityAspect(Enum):
    """Different aspects of audio quality"""
    OVERALL = "overall"
    CLARITY = "clarity"
    LOUDNESS = "loudness"
    DYNAMIC_RANGE = "dynamic_range"
    FREQUENCY_RESPONSE = "frequency_response"
    NOISE_LEVEL = "noise_level"
    DISTORTION = "distortion"
    STEREO_IMAGING = "stereo_imaging"
    TEMPORAL_ARTIFACTS = "temporal_artifacts"
    COMPRESSION_QUALITY = "compression_quality"


class QualityGrade(Enum):
    """Quality grades"""
    EXCELLENT = "excellent"     # 9.0-10.0
    VERY_GOOD = "very_good"    # 8.0-8.9
    GOOD = "good"              # 7.0-7.9
    FAIR = "fair"              # 6.0-6.9
    POOR = "poor"              # 4.0-5.9
    VERY_POOR = "very_poor"    # 0.0-3.9


@dataclass
class QualityMetric:
    """Individual quality metric result"""
    aspect: QualityAspect
    score: float  # 0.0 to 10.0
    grade: QualityGrade
    description: str
    recommendations: List[str]
    technical_details: Dict[str, Any]


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    overall_score: float
    overall_grade: QualityGrade
    metrics: Dict[QualityAspect, QualityMetric]
    summary: str
    recommendations: List[str]
    technical_analysis: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]


class PerceptualQualityAnalyzer:
    """
    👂 Perceptual Quality Analysis
    
    Human-perceptual quality assessment:
    - Psychoacoustic modeling
    - Perceptual loudness analysis
    - Frequency masking evaluation
    - Temporal masking assessment
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        
        # Psychoacoustic model parameters
        self.bark_scale_edges = self._init_bark_scale()
        self.masking_thresholds = self._init_masking_thresholds()
        
        logger.info("PerceptualQualityAnalyzer initialized")
    
    def _init_bark_scale(self) -> np.ndarray:
        """Initialize Bark scale frequency edges"""
        # Standard Bark scale frequencies (Hz)
        bark_edges = np.array([
            0, 100, 200, 300, 400, 510, 630, 770, 920, 1080,
            1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700,
            4400, 5300, 6400, 7700, 9500, 12000, 15500, 22050
        ])
        return bark_edges
    
    def _init_masking_thresholds(self) -> Dict[str, float]:
        """Initialize masking threshold parameters"""
        return {
            'tonality_threshold': 0.5,
            'simultaneous_masking_slope': 15.0,  # dB/Bark
            'temporal_masking_decay': 0.1,       # Time constant
            'quiet_threshold': -60.0             # dB
        }
    
    async def analyze_perceptual_quality(self,
                                       audio_data: np.ndarray,
                                       sample_rate: int) -> Dict[str, float]:
        """Analyze perceptual quality aspects"""
        try:
            metrics = {}
            
            # Calculate STFT
            stft = librosa.stft(audio_data, hop_length=512, n_fft=2048)
            magnitude = np.abs(stft)
            
            # Perceptual loudness
            loudness_score = await self._analyze_perceptual_loudness(
                magnitude, sample_rate
            )
            metrics['perceptual_loudness'] = loudness_score
            
            # Frequency balance
            frequency_balance = await self._analyze_frequency_balance(
                magnitude, sample_rate
            )
            metrics['frequency_balance'] = frequency_balance
            
            # Spectral clarity
            spectral_clarity = await self._analyze_spectral_clarity(
                magnitude, sample_rate
            )
            metrics['spectral_clarity'] = spectral_clarity
            
            # Temporal smoothness
            temporal_smoothness = await self._analyze_temporal_smoothness(
                magnitude
            )
            metrics['temporal_smoothness'] = temporal_smoothness
            
            return metrics
            
        except Exception as e:
            logger.error(f"Perceptual quality analysis failed: {e}")
            return {}
    
    async def _analyze_perceptual_loudness(self,
                                         magnitude: np.ndarray,
                                         sample_rate: int) -> float:
        """Analyze perceptual loudness using psychoacoustic principles"""
        try:
            # Convert to Bark scale bands
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=magnitude.shape[0]*2-1)
            
            # Calculate energy in each Bark band
            bark_energies = []
            for i in range(len(self.bark_scale_edges) - 1):
                low_freq = self.bark_scale_edges[i]
                high_freq = self.bark_scale_edges[i + 1]
                
                # Find frequency indices
                low_idx = np.argmin(np.abs(freqs - low_freq))
                high_idx = np.argmin(np.abs(freqs - high_freq))
                
                if high_idx > low_idx:
                    band_energy = np.mean(magnitude[low_idx:high_idx] ** 2)
                    bark_energies.append(band_energy)
                else:
                    bark_energies.append(0.0)
            
            bark_energies = np.array(bark_energies)
            
            # Apply loudness weighting (simplified equal-loudness contour)
            loudness_weights = self._get_loudness_weights()
            weighted_energies = bark_energies * loudness_weights[:len(bark_energies)]
            
            # Calculate total loudness
            total_loudness = np.sum(weighted_energies)
            
            # Normalize to 0-10 scale
            if total_loudness > 0:
                loudness_db = 10 * np.log10(total_loudness + 1e-10)
                # Map dB range to 0-10 quality score
                normalized_score = np.clip((loudness_db + 60) / 80 * 10, 0, 10)
            else:
                normalized_score = 0.0
            
            return float(normalized_score)
            
        except Exception as e:
            logger.error(f"Perceptual loudness analysis failed: {e}")
            return 5.0  # Default neutral score
    
    def _get_loudness_weights(self) -> np.ndarray:
        """Get loudness weighting based on equal-loudness contours"""
        # Simplified A-weighting-like curve for Bark bands
        # Real implementation would use ISO 226 standard
        weights = np.array([
            0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2,
            0.1, 0.05, 0.02, 0.01, 0.005
        ])
        return weights
    
    async def _analyze_frequency_balance(self,
                                       magnitude: np.ndarray,
                                       sample_rate: int) -> float:
        """Analyze frequency balance across spectrum"""
        try:
            # Define frequency bands (bass, mids, treble)
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=magnitude.shape[0]*2-1)
            
            # Calculate energy in different bands
            bass_energy = self._calculate_band_energy(magnitude, freqs, 20, 250)
            low_mid_energy = self._calculate_band_energy(magnitude, freqs, 250, 1000)
            high_mid_energy = self._calculate_band_energy(magnitude, freqs, 1000, 4000)
            treble_energy = self._calculate_band_energy(magnitude, freqs, 4000, 20000)
            
            # Calculate balance score based on energy distribution
            total_energy = bass_energy + low_mid_energy + high_mid_energy + treble_energy
            
            if total_energy > 0:
                bass_ratio = bass_energy / total_energy
                mid_ratio = (low_mid_energy + high_mid_energy) / total_energy
                treble_ratio = treble_energy / total_energy
                
                # Ideal ratios (can be adjusted based on genre/content)
                ideal_bass = 0.3
                ideal_mid = 0.5
                ideal_treble = 0.2
                
                # Calculate deviation from ideal
                bass_dev = abs(bass_ratio - ideal_bass)
                mid_dev = abs(mid_ratio - ideal_mid)
                treble_dev = abs(treble_ratio - ideal_treble)
                
                total_deviation = bass_dev + mid_dev + treble_dev
                balance_score = max(0, 10 - total_deviation * 20)
            else:
                balance_score = 0.0
            
            return float(balance_score)
            
        except Exception as e:
            logger.error(f"Frequency balance analysis failed: {e}")
            return 5.0
    
    def _calculate_band_energy(self,
                             magnitude: np.ndarray,
                             freqs: np.ndarray,
                             low_freq: float,
                             high_freq: float) -> float:
        """Calculate energy in a frequency band"""
        low_idx = np.argmin(np.abs(freqs - low_freq))
        high_idx = np.argmin(np.abs(freqs - high_freq))
        
        if high_idx > low_idx:
            return np.mean(magnitude[low_idx:high_idx] ** 2)
        else:
            return 0.0
    
    async def _analyze_spectral_clarity(self,
                                      magnitude: np.ndarray,
                                      sample_rate: int) -> float:
        """Analyze spectral clarity and definition"""
        try:
            # Calculate spectral centroid variation
            spectral_centroid = []
            for frame in magnitude.T:
                freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=len(frame)*2-1)
                if np.sum(frame) > 0:
                    centroid = np.sum(freqs * frame) / np.sum(frame)
                    spectral_centroid.append(centroid)
                else:
                    spectral_centroid.append(0)
            
            spectral_centroid = np.array(spectral_centroid)
            
            # Calculate spectral rolloff variation
            spectral_rolloff = []
            for frame in magnitude.T:
                rolloff = librosa.feature.spectral_rolloff(
                    S=frame.reshape(-1, 1), sr=sample_rate
                )[0, 0]
                spectral_rolloff.append(rolloff)
            
            spectral_rolloff = np.array(spectral_rolloff)
            
            # Clarity is inversely related to variation in spectral features
            centroid_variation = np.std(spectral_centroid) / (np.mean(spectral_centroid) + 1)
            rolloff_variation = np.std(spectral_rolloff) / (np.mean(spectral_rolloff) + 1)
            
            # Convert variation to clarity score
            clarity_score = 10 - min(10, (centroid_variation + rolloff_variation) * 5)
            
            return float(max(0, clarity_score))
            
        except Exception as e:
            logger.error(f"Spectral clarity analysis failed: {e}")
            return 5.0
    
    async def _analyze_temporal_smoothness(self, magnitude: np.ndarray) -> float:
        """Analyze temporal smoothness of the audio"""
        try:
            # Calculate frame-to-frame energy variations
            energy_per_frame = np.sum(magnitude ** 2, axis=0)
            
            if len(energy_per_frame) > 1:
                # Calculate energy differences between consecutive frames
                energy_diffs = np.diff(energy_per_frame)
                
                # Normalize by mean energy
                mean_energy = np.mean(energy_per_frame)
                if mean_energy > 0:
                    normalized_diffs = energy_diffs / mean_energy
                    
                    # Smoothness is inversely related to variation
                    smoothness_metric = 1.0 / (1.0 + np.std(normalized_diffs))
                    smoothness_score = smoothness_metric * 10
                else:
                    smoothness_score = 0.0
            else:
                smoothness_score = 5.0  # Neutral for single frame
            
            return float(np.clip(smoothness_score, 0, 10))
            
        except Exception as e:
            logger.error(f"Temporal smoothness analysis failed: {e}")
            return 5.0


class TechnicalQualityAnalyzer:
    """
    🔧 Technical Quality Analysis
    
    Objective technical quality assessment:
    - SNR and dynamic range
    - THD+N analysis
    - Frequency response evaluation
    - Clipping and distortion detection
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        
        logger.info("TechnicalQualityAnalyzer initialized")
    
    async def analyze_technical_quality(self,
                                      audio_data: np.ndarray,
                                      sample_rate: int) -> Dict[str, float]:
        """Analyze technical quality aspects"""
        try:
            metrics = {}
            
            # Signal-to-noise ratio
            snr_score = await self._analyze_snr(audio_data)
            metrics['snr'] = snr_score
            
            # Dynamic range
            dynamic_range_score = await self._analyze_dynamic_range(audio_data)
            metrics['dynamic_range'] = dynamic_range_score
            
            # THD+N (Total Harmonic Distortion + Noise)
            thd_score = await self._analyze_thd_n(audio_data, sample_rate)
            metrics['thd_n'] = thd_score
            
            # Clipping detection
            clipping_score = await self._analyze_clipping(audio_data)
            metrics['clipping'] = clipping_score
            
            # Frequency response flatness
            flatness_score = await self._analyze_frequency_flatness(audio_data, sample_rate)
            metrics['frequency_flatness'] = flatness_score
            
            # Peak-to-RMS ratio
            peak_rms_score = await self._analyze_peak_rms_ratio(audio_data)
            metrics['peak_rms_ratio'] = peak_rms_score
            
            return metrics
            
        except Exception as e:
            logger.error(f"Technical quality analysis failed: {e}")
            return {}
    
    async def _analyze_snr(self, audio_data: np.ndarray) -> float:
        """Analyze signal-to-noise ratio"""
        try:
            # Simple SNR estimation using quiet segments
            # Real implementation would use more sophisticated noise estimation
            
            # Calculate RMS energy
            rms_energy = np.sqrt(np.mean(audio_data ** 2))
            
            # Estimate noise floor using lowest 10% of energy values
            frame_size = int(0.1 * len(audio_data))  # 100ms frames
            frame_energies = []
            
            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_data[i:i + frame_size]
                frame_rms = np.sqrt(np.mean(frame ** 2))
                frame_energies.append(frame_rms)
            
            frame_energies = np.array(frame_energies)
            
            # Estimate noise floor
            noise_floor = np.percentile(frame_energies, 10)
            
            # Calculate SNR
            if noise_floor > 0 and rms_energy > noise_floor:
                snr_db = 20 * np.log10(rms_energy / noise_floor)
                
                # Convert SNR to quality score (0-10)
                # Good audio typically has SNR > 60dB
                snr_score = min(10, max(0, (snr_db - 20) / 60 * 10))
            else:
                snr_score = 0.0
            
            return float(snr_score)
            
        except Exception as e:
            logger.error(f"SNR analysis failed: {e}")
            return 5.0
    
    async def _analyze_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Analyze dynamic range"""
        try:
            # Calculate peak and RMS levels
            peak_level = np.max(np.abs(audio_data))
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            
            if rms_level > 0:
                # Dynamic range in dB
                dynamic_range_db = 20 * np.log10(peak_level / rms_level)
                
                # Quality score based on dynamic range
                # Good music typically has 12-20dB dynamic range
                if dynamic_range_db >= 15:
                    dr_score = 10.0
                elif dynamic_range_db >= 10:
                    dr_score = 8.0 + (dynamic_range_db - 10) / 5 * 2
                elif dynamic_range_db >= 5:
                    dr_score = 5.0 + (dynamic_range_db - 5) / 5 * 3
                else:
                    dr_score = dynamic_range_db
                
                dr_score = max(0, min(10, dr_score))
            else:
                dr_score = 0.0
            
            return float(dr_score)
            
        except Exception as e:
            logger.error(f"Dynamic range analysis failed: {e}")
            return 5.0
    
    async def _analyze_thd_n(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Analyze Total Harmonic Distortion + Noise"""
        try:
            # Simplified THD+N analysis
            # Real implementation would use sine wave analysis
            
            # Calculate spectral content
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft[:len(fft)//2])
            freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)[:len(magnitude)]
            
            # Find peaks (fundamental and harmonics)
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(magnitude, height=np.max(magnitude) * 0.1)
            
            if len(peaks) > 0:
                # Fundamental frequency (highest peak)
                fundamental_idx = peaks[np.argmax(magnitude[peaks])]
                fundamental_freq = freqs[fundamental_idx]
                fundamental_power = magnitude[fundamental_idx] ** 2
                
                # Find harmonics
                harmonic_power = 0
                for harmonic in range(2, 6):  # 2nd to 5th harmonics
                    harmonic_freq = fundamental_freq * harmonic
                    harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
                    harmonic_power += magnitude[harmonic_idx] ** 2
                
                # Calculate THD
                if fundamental_power > 0:
                    thd = np.sqrt(harmonic_power / fundamental_power)
                    thd_percent = thd * 100
                    
                    # Convert to quality score
                    if thd_percent <= 0.1:
                        thd_score = 10.0
                    elif thd_percent <= 1.0:
                        thd_score = 10 - thd_percent * 9 / 0.9
                    else:
                        thd_score = max(0, 1 - (thd_percent - 1) / 4)
                else:
                    thd_score = 5.0
            else:
                thd_score = 5.0
            
            return float(max(0, min(10, thd_score)))
            
        except Exception as e:
            logger.error(f"THD+N analysis failed: {e}")
            return 5.0
    
    async def _analyze_clipping(self, audio_data: np.ndarray) -> float:
        """Analyze clipping artifacts"""
        try:
            # Detect hard clipping
            max_val = np.max(np.abs(audio_data))
            clipping_threshold = 0.99  # 99% of full scale
            
            # Count samples at or near maximum
            clipped_samples = np.sum(np.abs(audio_data) >= clipping_threshold * max_val)
            clipping_percentage = clipped_samples / len(audio_data) * 100
            
            # Quality score based on clipping percentage
            if clipping_percentage == 0:
                clipping_score = 10.0
            elif clipping_percentage <= 0.1:
                clipping_score = 8.0
            elif clipping_percentage <= 0.5:
                clipping_score = 5.0
            elif clipping_percentage <= 1.0:
                clipping_score = 2.0
            else:
                clipping_score = 0.0
            
            return float(clipping_score)
            
        except Exception as e:
            logger.error(f"Clipping analysis failed: {e}")
            return 5.0
    
    async def _analyze_frequency_flatness(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int) -> float:
        """Analyze frequency response flatness"""
        try:
            # Calculate power spectral density
            freqs, psd = signal.welch(audio_data, sample_rate, nperseg=2048)
            
            # Focus on audible range (20Hz - 20kHz)
            audible_mask = (freqs >= 20) & (freqs <= 20000)
            audible_freqs = freqs[audible_mask]
            audible_psd = psd[audible_mask]
            
            if len(audible_psd) > 0:
                # Calculate smoothed PSD (octave bands)
                octave_bands = self._get_octave_bands(audible_freqs)
                band_energies = []
                
                for low_freq, high_freq in octave_bands:
                    band_mask = (audible_freqs >= low_freq) & (audible_freqs <= high_freq)
                    if np.any(band_mask):
                        band_energy = np.mean(audible_psd[band_mask])
                        band_energies.append(band_energy)
                
                if band_energies:
                    band_energies = np.array(band_energies)
                    
                    # Calculate flatness (inverse of variation)
                    if np.mean(band_energies) > 0:
                        variation_db = 20 * np.log10(
                            np.std(band_energies) / np.mean(band_energies) + 1e-10
                        )
                        
                        # Convert to quality score
                        flatness_score = max(0, 10 - abs(variation_db) / 3)
                    else:
                        flatness_score = 0.0
                else:
                    flatness_score = 5.0
            else:
                flatness_score = 5.0
            
            return float(max(0, min(10, flatness_score)))
            
        except Exception as e:
            logger.error(f"Frequency flatness analysis failed: {e}")
            return 5.0
    
    def _get_octave_bands(self, freqs: np.ndarray) -> List[Tuple[float, float]]:
        """Get octave band frequency ranges"""
        # Standard octave bands
        center_freqs = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        bands = []
        
        for center in center_freqs:
            if center > np.max(freqs):
                break
            
            low = center / np.sqrt(2)
            high = center * np.sqrt(2)
            
            # Ensure we don't exceed frequency bounds
            low = max(low, np.min(freqs))
            high = min(high, np.max(freqs))
            
            if low < high:
                bands.append((low, high))
        
        return bands
    
    async def _analyze_peak_rms_ratio(self, audio_data: np.ndarray) -> float:
        """Analyze peak-to-RMS ratio"""
        try:
            peak_level = np.max(np.abs(audio_data))
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            
            if rms_level > 0:
                peak_rms_ratio = peak_level / rms_level
                
                # Good audio typically has peak/RMS ratio between 3-6
                if 3 <= peak_rms_ratio <= 6:
                    ratio_score = 10.0
                elif 2 <= peak_rms_ratio < 3:
                    ratio_score = 5.0 + (peak_rms_ratio - 2) * 5
                elif 6 < peak_rms_ratio <= 10:
                    ratio_score = 10.0 - (peak_rms_ratio - 6) * 2
                else:
                    ratio_score = max(0, 2 - abs(peak_rms_ratio - 5) / 5)
            else:
                ratio_score = 0.0
            
            return float(max(0, min(10, ratio_score)))
            
        except Exception as e:
            logger.error(f"Peak-RMS ratio analysis failed: {e}")
            return 5.0


class AudioQualityAssessor:
    """
    🎯 Comprehensive Audio Quality Assessor
    
    Professional quality assessment system:
    - Perceptual and technical analysis
    - Multi-dimensional quality scoring
    - Detailed recommendations
    - Comparative quality analysis
    - Optimization suggestions
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.audio_processor = AudioProcessor(config)
        
        # Initialize analyzers
        self.perceptual_analyzer = PerceptualQualityAnalyzer(config)
        self.technical_analyzer = TechnicalQualityAnalyzer(config)
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityGrade.EXCELLENT: 9.0,
            QualityGrade.VERY_GOOD: 8.0,
            QualityGrade.GOOD: 7.0,
            QualityGrade.FAIR: 6.0,
            QualityGrade.POOR: 4.0,
            QualityGrade.VERY_POOR: 0.0
        }
        
        logger.info("AudioQualityAssessor initialized")
    
    async def assess_quality(self,
                           audio_data: np.ndarray,
                           sample_rate: int,
                           reference_audio: Optional[np.ndarray] = None) -> QualityReport:
        """
        Comprehensive audio quality assessment
        
        Args:
            audio_data: Audio samples to assess
            sample_rate: Sample rate
            reference_audio: Optional reference for comparison
            
        Returns:
            Detailed quality report
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("Starting comprehensive audio quality assessment")
            
            # Perform perceptual analysis
            perceptual_metrics = await self.perceptual_analyzer.analyze_perceptual_quality(
                audio_data, sample_rate
            )
            
            # Perform technical analysis
            technical_metrics = await self.technical_analyzer.analyze_technical_quality(
                audio_data, sample_rate
            )
            
            # Additional quality metrics
            additional_metrics = await self._analyze_additional_metrics(
                audio_data, sample_rate
            )
            
            # Combine all metrics
            all_metrics = {**perceptual_metrics, **technical_metrics, **additional_metrics}
            
            # Generate quality metrics for each aspect
            quality_metrics = {}
            
            # Clarity
            clarity_components = ['spectral_clarity', 'frequency_flatness', 'thd_n']
            clarity_score = self._calculate_composite_score(all_metrics, clarity_components)
            quality_metrics[QualityAspect.CLARITY] = QualityMetric(
                aspect=QualityAspect.CLARITY,
                score=clarity_score,
                grade=self._score_to_grade(clarity_score),
                description=f"Audio clarity score: {clarity_score:.1f}/10",
                recommendations=self._get_clarity_recommendations(clarity_score, all_metrics),
                technical_details={k: all_metrics.get(k, 0) for k in clarity_components}
            )
            
            # Loudness
            loudness_components = ['perceptual_loudness', 'peak_rms_ratio', 'dynamic_range']
            loudness_score = self._calculate_composite_score(all_metrics, loudness_components)
            quality_metrics[QualityAspect.LOUDNESS] = QualityMetric(
                aspect=QualityAspect.LOUDNESS,
                score=loudness_score,
                grade=self._score_to_grade(loudness_score),
                description=f"Loudness quality score: {loudness_score:.1f}/10",
                recommendations=self._get_loudness_recommendations(loudness_score, all_metrics),
                technical_details={k: all_metrics.get(k, 0) for k in loudness_components}
            )
            
            # Dynamic Range
            dr_score = all_metrics.get('dynamic_range', 5.0)
            quality_metrics[QualityAspect.DYNAMIC_RANGE] = QualityMetric(
                aspect=QualityAspect.DYNAMIC_RANGE,
                score=dr_score,
                grade=self._score_to_grade(dr_score),
                description=f"Dynamic range score: {dr_score:.1f}/10",
                recommendations=self._get_dynamic_range_recommendations(dr_score),
                technical_details={'dynamic_range_db': all_metrics.get('dynamic_range_db', 0)}
            )
            
            # Frequency Response
            freq_components = ['frequency_balance', 'frequency_flatness']
            freq_score = self._calculate_composite_score(all_metrics, freq_components)
            quality_metrics[QualityAspect.FREQUENCY_RESPONSE] = QualityMetric(
                aspect=QualityAspect.FREQUENCY_RESPONSE,
                score=freq_score,
                grade=self._score_to_grade(freq_score),
                description=f"Frequency response score: {freq_score:.1f}/10",
                recommendations=self._get_frequency_recommendations(freq_score, all_metrics),
                technical_details={k: all_metrics.get(k, 0) for k in freq_components}
            )
            
            # Noise Level
            noise_components = ['snr', 'noise_level']
            noise_score = self._calculate_composite_score(all_metrics, noise_components)
            quality_metrics[QualityAspect.NOISE_LEVEL] = QualityMetric(
                aspect=QualityAspect.NOISE_LEVEL,
                score=noise_score,
                grade=self._score_to_grade(noise_score),
                description=f"Noise level score: {noise_score:.1f}/10",
                recommendations=self._get_noise_recommendations(noise_score, all_metrics),
                technical_details={k: all_metrics.get(k, 0) for k in noise_components}
            )
            
            # Distortion
            distortion_components = ['thd_n', 'clipping']
            distortion_score = self._calculate_composite_score(all_metrics, distortion_components)
            quality_metrics[QualityAspect.DISTORTION] = QualityMetric(
                aspect=QualityAspect.DISTORTION,
                score=distortion_score,
                grade=self._score_to_grade(distortion_score),
                description=f"Distortion score: {distortion_score:.1f}/10",
                recommendations=self._get_distortion_recommendations(distortion_score, all_metrics),
                technical_details={k: all_metrics.get(k, 0) for k in distortion_components}
            )
            
            # Temporal Artifacts
            temporal_score = all_metrics.get('temporal_smoothness', 5.0)
            quality_metrics[QualityAspect.TEMPORAL_ARTIFACTS] = QualityMetric(
                aspect=QualityAspect.TEMPORAL_ARTIFACTS,
                score=temporal_score,
                grade=self._score_to_grade(temporal_score),
                description=f"Temporal quality score: {temporal_score:.1f}/10",
                recommendations=self._get_temporal_recommendations(temporal_score),
                technical_details={'temporal_smoothness': temporal_score}
            )
            
            # Calculate overall score
            aspect_scores = [metric.score for metric in quality_metrics.values()]
            overall_score = np.mean(aspect_scores)
            overall_grade = self._score_to_grade(overall_score)
            
            # Generate summary and recommendations
            summary = self._generate_summary(overall_score, overall_grade, quality_metrics)
            recommendations = self._generate_overall_recommendations(quality_metrics)
            
            processing_time = time.time() - start_time
            
            # Create report
            report = QualityReport(
                overall_score=overall_score,
                overall_grade=overall_grade,
                metrics=quality_metrics,
                summary=summary,
                recommendations=recommendations,
                technical_analysis=all_metrics,
                processing_time=processing_time,
                metadata={
                    'sample_rate': sample_rate,
                    'duration': len(audio_data) / sample_rate,
                    'channels': 1 if audio_data.ndim == 1 else audio_data.shape[0],
                    'peak_level': float(np.max(np.abs(audio_data))),
                    'rms_level': float(np.sqrt(np.mean(audio_data ** 2)))
                }
            )
            
            logger.info(f"Quality assessment completed: {overall_score:.1f}/10 ({overall_grade.value})")
            return report
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            
            # Return minimal report on error
            return QualityReport(
                overall_score=0.0,
                overall_grade=QualityGrade.VERY_POOR,
                metrics={},
                summary=f"Quality assessment failed: {str(e)}",
                recommendations=["Unable to assess quality due to processing error"],
                technical_analysis={},
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    async def _analyze_additional_metrics(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int) -> Dict[str, float]:
        """Analyze additional quality metrics"""
        try:
            metrics = {}
            
            # Silence detection
            silence_ratio = await self._analyze_silence_ratio(audio_data)
            metrics['silence_ratio'] = silence_ratio
            
            # Stereo imaging (if stereo)
            if audio_data.ndim == 2:
                stereo_score = await self._analyze_stereo_imaging(audio_data)
                metrics['stereo_imaging'] = stereo_score
            
            # Noise level estimation
            noise_level = await self._estimate_noise_level(audio_data)
            metrics['noise_level'] = noise_level
            
            # Calculate actual dynamic range in dB
            peak_level = np.max(np.abs(audio_data))
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            if rms_level > 0:
                dr_db = 20 * np.log10(peak_level / rms_level)
                metrics['dynamic_range_db'] = dr_db
            
            return metrics
            
        except Exception as e:
            logger.error(f"Additional metrics analysis failed: {e}")
            return {}
    
    async def _analyze_silence_ratio(self, audio_data: np.ndarray) -> float:
        """Analyze ratio of silence in audio"""
        try:
            # Define silence threshold (e.g., -60dB)
            silence_threshold = 0.001  # About -60dB
            
            # Count silent samples
            silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
            silence_ratio = silent_samples / len(audio_data)
            
            # Convert to quality score (too much silence is bad)
            if silence_ratio <= 0.1:  # Less than 10% silence is good
                score = 10.0
            elif silence_ratio <= 0.3:  # 10-30% is acceptable
                score = 10.0 - (silence_ratio - 0.1) * 25
            else:  # More than 30% is poor
                score = max(0, 5.0 - (silence_ratio - 0.3) * 10)
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Silence analysis failed: {e}")
            return 5.0
    
    async def _analyze_stereo_imaging(self, stereo_audio: np.ndarray) -> float:
        """Analyze stereo imaging quality"""
        try:
            left_channel = stereo_audio[0, :]
            right_channel = stereo_audio[1, :]
            
            # Calculate correlation between channels
            correlation = np.corrcoef(left_channel, right_channel)[0, 1]
            
            # Calculate level difference
            left_rms = np.sqrt(np.mean(left_channel ** 2))
            right_rms = np.sqrt(np.mean(right_channel ** 2))
            
            if left_rms > 0 and right_rms > 0:
                level_diff_db = abs(20 * np.log10(left_rms / right_rms))
            else:
                level_diff_db = 0.0
            
            # Good stereo should have moderate correlation (0.3-0.8) and balanced levels
            correlation_score = 10.0
            if correlation < 0.1 or correlation > 0.95:
                correlation_score = max(0, 10 - abs(correlation - 0.5) * 20)
            
            level_score = max(0, 10 - level_diff_db)
            
            stereo_score = (correlation_score + level_score) / 2
            
            return float(stereo_score)
            
        except Exception as e:
            logger.error(f"Stereo imaging analysis failed: {e}")
            return 5.0
    
    async def _estimate_noise_level(self, audio_data: np.ndarray) -> float:
        """Estimate background noise level"""
        try:
            # Use minimum RMS in sliding windows as noise estimate
            window_size = int(0.1 * len(audio_data))  # 100ms windows
            window_rms = []
            
            for i in range(0, len(audio_data) - window_size, window_size // 2):
                window = audio_data[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                window_rms.append(rms)
            
            if window_rms:
                # Noise level is estimated as 10th percentile of RMS values
                noise_rms = np.percentile(window_rms, 10)
                
                if noise_rms > 0:
                    noise_db = 20 * np.log10(noise_rms)
                    
                    # Convert to quality score (lower noise is better)
                    if noise_db <= -60:
                        score = 10.0
                    elif noise_db <= -40:
                        score = 10.0 - (noise_db + 60) * 0.25
                    else:
                        score = max(0, 5.0 - (noise_db + 40) * 0.1)
                else:
                    score = 10.0  # No noise detected
            else:
                score = 5.0
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Noise level estimation failed: {e}")
            return 5.0
    
    def _calculate_composite_score(self,
                                 metrics: Dict[str, float],
                                 components: List[str],
                                 weights: Optional[List[float]] = None) -> float:
        """Calculate weighted composite score from multiple components"""
        if weights is None:
            weights = [1.0] * len(components)
        
        if len(weights) != len(components):
            weights = [1.0] * len(components)
        
        total_weight = 0
        weighted_sum = 0
        
        for component, weight in zip(components, weights):
            if component in metrics:
                weighted_sum += metrics[component] * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 5.0  # Default neutral score
    
    def _score_to_grade(self, score: float) -> QualityGrade:
        """Convert numeric score to quality grade"""
        if score >= 9.0:
            return QualityGrade.EXCELLENT
        elif score >= 8.0:
            return QualityGrade.VERY_GOOD
        elif score >= 7.0:
            return QualityGrade.GOOD
        elif score >= 6.0:
            return QualityGrade.FAIR
        elif score >= 4.0:
            return QualityGrade.POOR
        else:
            return QualityGrade.VERY_POOR
    
    def _get_clarity_recommendations(self, score: float, metrics: Dict[str, float]) -> List[str]:
        """Get recommendations for improving clarity"""
        recommendations = []
        
        if score < 7.0:
            if metrics.get('thd_n', 10) < 6:
                recommendations.append("Reduce harmonic distortion with better recording equipment")
            
            if metrics.get('frequency_flatness', 5) < 6:
                recommendations.append("Apply EQ to improve frequency balance")
            
            if metrics.get('spectral_clarity', 5) < 6:
                recommendations.append("Use noise reduction to improve spectral clarity")
            
            recommendations.append("Consider re-recording with better microphone placement")
        
        return recommendations
    
    def _get_loudness_recommendations(self, score: float, metrics: Dict[str, float]) -> List[str]:
        """Get recommendations for improving loudness"""
        recommendations = []
        
        if score < 7.0:
            if metrics.get('dynamic_range', 5) < 6:
                recommendations.append("Increase dynamic range to improve perceived quality")
            
            if metrics.get('peak_rms_ratio', 5) < 6:
                recommendations.append("Optimize peak-to-RMS ratio with compression")
            
            recommendations.append("Consider professional mastering for optimal loudness")
        
        return recommendations
    
    def _get_dynamic_range_recommendations(self, score: float) -> List[str]:
        """Get recommendations for improving dynamic range"""
        recommendations = []
        
        if score < 7.0:
            recommendations.extend([
                "Reduce excessive compression to preserve dynamics",
                "Use multiband compression for better dynamic control",
                "Consider the target playback environment when setting dynamic range"
            ])
        
        return recommendations
    
    def _get_frequency_recommendations(self, score: float, metrics: Dict[str, float]) -> List[str]:
        """Get recommendations for improving frequency response"""
        recommendations = []
        
        if score < 7.0:
            recommendations.extend([
                "Apply corrective EQ to improve frequency balance",
                "Check for room acoustics issues during recording",
                "Use reference monitors for better frequency accuracy"
            ])
        
        return recommendations
    
    def _get_noise_recommendations(self, score: float, metrics: Dict[str, float]) -> List[str]:
        """Get recommendations for reducing noise"""
        recommendations = []
        
        if score < 7.0:
            recommendations.extend([
                "Apply noise reduction processing",
                "Improve recording environment acoustics",
                "Use better shielding and equipment to reduce noise",
                "Consider re-recording in a quieter environment"
            ])
        
        return recommendations
    
    def _get_distortion_recommendations(self, score: float, metrics: Dict[str, float]) -> List[str]:
        """Get recommendations for reducing distortion"""
        recommendations = []
        
        if score < 7.0:
            if metrics.get('clipping', 10) < 7:
                recommendations.append("Reduce input levels to prevent clipping")
            
            if metrics.get('thd_n', 10) < 7:
                recommendations.append("Use higher quality recording equipment")
            
            recommendations.extend([
                "Check gain staging throughout the signal chain",
                "Use limiters to prevent digital clipping"
            ])
        
        return recommendations
    
    def _get_temporal_recommendations(self, score: float) -> List[str]:
        """Get recommendations for improving temporal quality"""
        recommendations = []
        
        if score < 7.0:
            recommendations.extend([
                "Check for timing issues in multi-track recordings",
                "Use de-clicking tools to remove temporal artifacts",
                "Ensure stable clock synchronization in digital recordings"
            ])
        
        return recommendations
    
    def _generate_summary(self,
                        overall_score: float,
                        overall_grade: QualityGrade,
                        metrics: Dict[QualityAspect, QualityMetric]) -> str:
        """Generate quality assessment summary"""
        summary_parts = [
            f"Overall Quality: {overall_score:.1f}/10 ({overall_grade.value.replace('_', ' ').title()})"
        ]
        
        # Highlight best and worst aspects
        scores = {aspect: metric.score for aspect, metric in metrics.items()}
        best_aspect = max(scores.keys(), key=lambda k: scores[k])
        worst_aspect = min(scores.keys(), key=lambda k: scores[k])
        
        summary_parts.append(
            f"Strongest aspect: {best_aspect.value.replace('_', ' ').title()} ({scores[best_aspect]:.1f}/10)"
        )
        
        summary_parts.append(
            f"Weakest aspect: {worst_aspect.value.replace('_', ' ').title()} ({scores[worst_aspect]:.1f}/10)"
        )
        
        # Add grade-specific comments
        if overall_grade in [QualityGrade.EXCELLENT, QualityGrade.VERY_GOOD]:
            summary_parts.append("This audio demonstrates professional quality standards.")
        elif overall_grade == QualityGrade.GOOD:
            summary_parts.append("This audio has good quality with minor areas for improvement.")
        elif overall_grade == QualityGrade.FAIR:
            summary_parts.append("This audio is acceptable but would benefit from significant improvements.")
        else:
            summary_parts.append("This audio requires substantial improvement to meet quality standards.")
        
        return " ".join(summary_parts)
    
    def _generate_overall_recommendations(self,
                                        metrics: Dict[QualityAspect, QualityMetric]) -> List[str]:
        """Generate overall improvement recommendations"""
        all_recommendations = []
        
        # Collect recommendations from all aspects, prioritizing worst scores
        sorted_metrics = sorted(metrics.items(), key=lambda x: x[1].score)
        
        for aspect, metric in sorted_metrics:
            if metric.score < 8.0:  # Only include recommendations for sub-optimal aspects
                all_recommendations.extend(metric.recommendations)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        # Limit to top 10 recommendations
        return unique_recommendations[:10]
    
    async def compare_quality(self,
                            audio1: np.ndarray,
                            audio2: np.ndarray,
                            sample_rate: int) -> Dict[str, Any]:
        """Compare quality between two audio files"""
        try:
            # Assess both files
            report1 = await self.assess_quality(audio1, sample_rate)
            report2 = await self.assess_quality(audio2, sample_rate)
            
            # Calculate differences
            score_diff = report2.overall_score - report1.overall_score
            
            aspect_comparisons = {}
            for aspect in QualityAspect:
                if aspect in report1.metrics and aspect in report2.metrics:
                    diff = report2.metrics[aspect].score - report1.metrics[aspect].score
                    aspect_comparisons[aspect.value] = {
                        'audio1_score': report1.metrics[aspect].score,
                        'audio2_score': report2.metrics[aspect].score,
                        'difference': diff,
                        'better': 'audio2' if diff > 0 else 'audio1' if diff < 0 else 'equal'
                    }
            
            return {
                'overall_comparison': {
                    'audio1_score': report1.overall_score,
                    'audio2_score': report2.overall_score,
                    'difference': score_diff,
                    'better_audio': 'audio2' if score_diff > 0 else 'audio1' if score_diff < 0 else 'equal'
                },
                'aspect_comparisons': aspect_comparisons,
                'summary': f"Audio 2 is {abs(score_diff):.1f} points "
                          f"{'better' if score_diff > 0 else 'worse' if score_diff < 0 else 'equal'} "
                          f"than Audio 1"
            }
            
        except Exception as e:
            logger.error(f"Quality comparison failed: {e}")
            return {'error': str(e)}
