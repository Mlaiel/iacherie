"""Quality Management System - Professional Audio Quality Control

Advanced quality assessment, optimization, and control system for audio format conversion.
Provides comprehensive quality metrics, optimization algorithms, and quality assurance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.stats import pearsonr
import librosa
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from datetime import datetime

from ..core.config import AudioConfig
from ..core.exceptions import QualityError
from .models import QualityProfile, QualityMetrics
from .config import QualityConfig

logger = logging.getLogger(__name__)


@dataclass
class QualityAnalysis:
    """Comprehensive quality analysis results"""    spectral_similarity: float
    dynamic_range_preservation: float
    frequency_response_accuracy: float
    noise_floor_level: float
    distortion_level: float
    stereo_imaging_quality: float
    overall_quality_score: float
    detailed_metrics: Dict[str, float]
    recommendations: List[str]


class QualityController:
    """    Professional Audio Quality Controller
    
    Advanced quality assessment and optimization system providing:
    - Multi-dimensional quality metrics calculation
    - Intelligent quality optimization algorithms
    - Real-time quality monitoring and alerting
    - Professional audio quality standards compliance
    """    
    def __init__(self, config: Optional[QualityConfig] = None):
        """Initialize quality controller"""        self.config = config or QualityConfig()
        self.quality_standards = self._load_quality_standards()
        self.analysis_cache: Dict[str, QualityAnalysis] = {}
        
    def _load_quality_standards(self) -> Dict[str, Dict[str, float]]:
        """Load professional quality standards"""        return {
            'broadcast': {
                'min_snr': 60.0,  # dB
                'max_thd': 0.1,   # %
                'frequency_response_tolerance': 0.5,  # dB
                'dynamic_range_min': 90.0,  # dB
                'stereo_separation_min': 40.0  # dB
            },
            'mastering': {
                'min_snr': 96.0,
                'max_thd': 0.01,
                'frequency_response_tolerance': 0.1,
                'dynamic_range_min': 110.0,
                'stereo_separation_min': 60.0
            },
            'streaming': {
                'min_snr': 40.0,
                'max_thd': 1.0,
                'frequency_response_tolerance': 2.0,
                'dynamic_range_min': 60.0,
                'stereo_separation_min': 20.0
            },
            'archival': {
                'min_snr': 120.0,
                'max_thd': 0.001,
                'frequency_response_tolerance': 0.05,
                'dynamic_range_min': 144.0,
                'stereo_separation_min': 80.0
            }
        }
    
    async def calculate_metrics(self,
                              original_audio: np.ndarray,
                              converted_audio: np.ndarray,
                              original_sr: int,
                              converted_sr: int,
                              quality_profile: Optional[QualityProfile] = None) -> QualityMetrics:
        """        Calculate comprehensive quality metrics comparing original and converted audio
        
        Args:
            original_audio: Original audio data
            converted_audio: Converted audio data
            original_sr: Original sample rate
            converted_sr: Converted sample rate
            quality_profile: Target quality profile
            
        Returns:
            Comprehensive quality metrics
        """        try:
            # Ensure both audio have same sample rate for comparison
            if original_sr != converted_sr:
                # Resample converted audio to original sample rate for comparison
                converted_audio = librosa.resample(
                    converted_audio, orig_sr=converted_sr, target_sr=original_sr
                )
            
            # Ensure same length
            min_length = min(len(original_audio), len(converted_audio))
            original_audio = original_audio[:min_length]
            converted_audio = converted_audio[:min_length]
            
            # Calculate individual metrics
            spectral_similarity = await self._calculate_spectral_similarity(
                original_audio, converted_audio, original_sr
            )
            
            dynamic_range_metrics = await self._calculate_dynamic_range_metrics(
                original_audio, converted_audio
            )
            
            frequency_metrics = await self._calculate_frequency_response_metrics(
                original_audio, converted_audio, original_sr
            )
            
            noise_metrics = await self._calculate_noise_metrics(
                original_audio, converted_audio, original_sr
            )
            
            distortion_metrics = await self._calculate_distortion_metrics(
                original_audio, converted_audio, original_sr
            )
            
            stereo_metrics = await self._calculate_stereo_metrics(
                original_audio, converted_audio
            ) if len(original_audio.shape) > 1 else {}
            
            # Calculate overall quality score
            overall_score = await self._calculate_overall_quality_score(
                spectral_similarity,
                dynamic_range_metrics,
                frequency_metrics,
                noise_metrics,
                distortion_metrics,
                stereo_metrics
            )
            
            # Compile detailed metrics
            detailed_metrics = {
                **spectral_similarity,
                **dynamic_range_metrics,
                **frequency_metrics,
                **noise_metrics,
                **distortion_metrics,
                **stereo_metrics
            }
            
            # Generate quality assessment
            assessment = await self._assess_quality_compliance(
                detailed_metrics, quality_profile
            )
            
            return QualityMetrics(
                overall_score=overall_score,
                spectral_similarity=spectral_similarity.get('correlation', 0.0),
                dynamic_range_preservation=dynamic_range_metrics.get('preservation', 0.0),
                frequency_response_accuracy=frequency_metrics.get('accuracy', 0.0),
                noise_floor_level=noise_metrics.get('floor_level', 0.0),
                distortion_level=distortion_metrics.get('thd', 0.0),
                stereo_imaging_quality=stereo_metrics.get('imaging_quality', 1.0),
                detailed_metrics=detailed_metrics,
                quality_assessment=assessment,
                compliance_report=await self._generate_compliance_report(
                    detailed_metrics, quality_profile
                )
            )
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return QualityMetrics(
                overall_score=0.0,
                error_message=str(e)
            )
    
    async def _calculate_spectral_similarity(self,
                                           original: np.ndarray,
                                           converted: np.ndarray,
                                           sample_rate: int) -> Dict[str, float]:
        """Calculate spectral similarity metrics"""        # Calculate spectrograms
        orig_stft = np.abs(librosa.stft(original))
        conv_stft = np.abs(librosa.stft(converted))
        
        # Ensure same shape
        min_shape = (
            min(orig_stft.shape[0], conv_stft.shape[0]),
            min(orig_stft.shape[1], conv_stft.shape[1])
        )
        orig_stft = orig_stft[:min_shape[0], :min_shape[1]]
        conv_stft = conv_stft[:min_shape[0], :min_shape[1]]
        
        # Calculate correlation
        correlation = np.corrcoef(
            orig_stft.flatten(),
            conv_stft.flatten()
        )[0, 1]
        
        # Calculate spectral centroid similarity
        orig_centroid = librosa.feature.spectral_centroid(y=original, sr=sample_rate)[0]
        conv_centroid = librosa.feature.spectral_centroid(y=converted, sr=sample_rate)[0]
        
        centroid_similarity = 1.0 - np.mean(np.abs(orig_centroid - conv_centroid)) / sample_rate * 2
        
        # Calculate spectral rolloff similarity
        orig_rolloff = librosa.feature.spectral_rolloff(y=original, sr=sample_rate)[0]
        conv_rolloff = librosa.feature.spectral_rolloff(y=converted, sr=sample_rate)[0]
        
        rolloff_similarity = 1.0 - np.mean(np.abs(orig_rolloff - conv_rolloff)) / sample_rate * 2
        
        return {
            'correlation': float(correlation if not np.isnan(correlation) else 0.0),
            'centroid_similarity': float(np.clip(centroid_similarity, 0.0, 1.0)),
            'rolloff_similarity': float(np.clip(rolloff_similarity, 0.0, 1.0)),
            'spectral_contrast': float(self._calculate_spectral_contrast_similarity(
                original, converted, sample_rate
            ))
        }
    
    async def _calculate_dynamic_range_metrics(self,
                                             original: np.ndarray,
                                             converted: np.ndarray) -> Dict[str, float]:
        """Calculate dynamic range preservation metrics"""        # Calculate RMS levels
        orig_rms = np.sqrt(np.mean(original**2))
        conv_rms = np.sqrt(np.mean(converted**2))
        
        # Calculate peak levels
        orig_peak = np.max(np.abs(original))
        conv_peak = np.max(np.abs(converted))
        
        # Calculate dynamic range
        orig_dr = 20 * np.log10(orig_peak / (orig_rms + 1e-10))
        conv_dr = 20 * np.log10(conv_peak / (conv_rms + 1e-10))
        
        # Calculate preservation ratio
        preservation = 1.0 - abs(orig_dr - conv_dr) / max(orig_dr, 1.0)
        
        # Calculate crest factor
        orig_crest = orig_peak / (orig_rms + 1e-10)
        conv_crest = conv_peak / (conv_rms + 1e-10)
        crest_preservation = 1.0 - abs(orig_crest - conv_crest) / max(orig_crest, 1.0)
        
        return {
            'preservation': float(np.clip(preservation, 0.0, 1.0)),
            'original_dr': float(orig_dr),
            'converted_dr': float(conv_dr),
            'crest_factor_preservation': float(np.clip(crest_preservation, 0.0, 1.0)),
            'rms_level_difference': float(20 * np.log10((conv_rms + 1e-10) / (orig_rms + 1e-10)))
        }
    
    async def _calculate_frequency_response_metrics(self,
                                                  original: np.ndarray,
                                                  converted: np.ndarray,
                                                  sample_rate: int) -> Dict[str, float]:
        """Calculate frequency response accuracy metrics"""        # Calculate frequency responses
        orig_freqs, orig_response = signal.welch(original, fs=sample_rate, nperseg=2048)
        conv_freqs, conv_response = signal.welch(converted, fs=sample_rate, nperseg=2048)
        
        # Ensure same frequency bins
        min_bins = min(len(orig_response), len(conv_response))
        orig_response = orig_response[:min_bins]
        conv_response = conv_response[:min_bins]
        
        # Calculate frequency response difference in dB
        response_diff = 10 * np.log10((conv_response + 1e-10) / (orig_response + 1e-10))
        
        # Calculate accuracy metrics
        mean_deviation = np.mean(np.abs(response_diff))
        max_deviation = np.max(np.abs(response_diff))
        
        # Focus on critical frequency ranges
        # Low frequencies (20-200 Hz)
        low_freq_mask = (orig_freqs >= 20) & (orig_freqs <= 200)
        low_freq_accuracy = 1.0 - np.mean(np.abs(response_diff[low_freq_mask])) / 6.0
        
        # Mid frequencies (200-2000 Hz)
        mid_freq_mask = (orig_freqs >= 200) & (orig_freqs <= 2000)
        mid_freq_accuracy = 1.0 - np.mean(np.abs(response_diff[mid_freq_mask])) / 3.0
        
        # High frequencies (2000-20000 Hz)
        high_freq_mask = (orig_freqs >= 2000) & (orig_freqs <= min(20000, sample_rate // 2))
        high_freq_accuracy = 1.0 - np.mean(np.abs(response_diff[high_freq_mask])) / 6.0
        
        # Overall accuracy
        accuracy = 1.0 - mean_deviation / 10.0  # Normalize to 0-1 scale
        
        return {
            'accuracy': float(np.clip(accuracy, 0.0, 1.0)),
            'mean_deviation_db': float(mean_deviation),
            'max_deviation_db': float(max_deviation),
            'low_freq_accuracy': float(np.clip(low_freq_accuracy, 0.0, 1.0)),
            'mid_freq_accuracy': float(np.clip(mid_freq_accuracy, 0.0, 1.0)),
            'high_freq_accuracy': float(np.clip(high_freq_accuracy, 0.0, 1.0))
        }
    
    async def _calculate_noise_metrics(self,
                                     original: np.ndarray,
                                     converted: np.ndarray,
                                     sample_rate: int) -> Dict[str, float]:
        """Calculate noise and SNR metrics"""        # Calculate noise floor (bottom 10% of signal energy)
        orig_sorted = np.sort(np.abs(original))
        conv_sorted = np.sort(np.abs(converted))
        
        orig_noise_floor = np.mean(orig_sorted[:len(orig_sorted) // 10])
        conv_noise_floor = np.mean(conv_sorted[:len(conv_sorted) // 10])
        
        # Calculate signal power (top 10% of signal energy)
        orig_signal = np.mean(orig_sorted[-len(orig_sorted) // 10:])
        conv_signal = np.mean(conv_sorted[-len(conv_sorted) // 10:])
        
        # Calculate SNR
        orig_snr = 20 * np.log10((orig_signal + 1e-10) / (orig_noise_floor + 1e-10))
        conv_snr = 20 * np.log10((conv_signal + 1e-10) / (conv_noise_floor + 1e-10))
        
        # Calculate noise floor level in dB
        noise_floor_level = 20 * np.log10(conv_noise_floor + 1e-10)
        
        # Calculate SNR preservation
        snr_preservation = 1.0 - abs(orig_snr - conv_snr) / max(orig_snr, 1.0)
        
        return {
            'floor_level': float(noise_floor_level),
            'snr_db': float(conv_snr),
            'snr_preservation': float(np.clip(snr_preservation, 0.0, 1.0)),
            'original_snr': float(orig_snr),
            'noise_increase_db': float(20 * np.log10((conv_noise_floor + 1e-10) / (orig_noise_floor + 1e-10)))
        }
    
    async def _calculate_distortion_metrics(self,
                                          original: np.ndarray,
                                          converted: np.ndarray,
                                          sample_rate: int) -> Dict[str, float]:
        """Calculate harmonic and intermodulation distortion metrics"""        # Calculate THD (Total Harmonic Distortion)
        thd = await self._calculate_thd(converted, sample_rate)
        
        # Calculate IMD (Intermodulation Distortion)
        imd = await self._calculate_imd(original, converted, sample_rate)
        
        # Calculate difference signal for distortion analysis
        if len(original) == len(converted):
            difference = converted - original
            distortion_level = np.sqrt(np.mean(difference**2)) / (np.sqrt(np.mean(original**2)) + 1e-10)
        else:
            distortion_level = 0.0
        
        return {
            'thd': float(thd),
            'imd': float(imd),
            'distortion_level': float(distortion_level),
            'distortion_db': float(20 * np.log10(distortion_level + 1e-10))
        }
    
    async def _calculate_stereo_metrics(self,
                                      original: np.ndarray,
                                      converted: np.ndarray) -> Dict[str, float]:
        """Calculate stereo imaging and separation metrics"""        if len(original.shape) < 2 or original.shape[1] < 2:
            return {}
        
        # Extract left and right channels
        orig_l, orig_r = original[:, 0], original[:, 1]
        conv_l, conv_r = converted[:, 0], converted[:, 1]
        
        # Calculate stereo separation
        orig_separation = np.corrcoef(orig_l, orig_r)[0, 1]
        conv_separation = np.corrcoef(conv_l, conv_r)[0, 1]
        
        # Calculate channel balance
        orig_balance = np.mean(np.abs(orig_l)) / (np.mean(np.abs(orig_r)) + 1e-10)
        conv_balance = np.mean(np.abs(conv_l)) / (np.mean(np.abs(conv_r)) + 1e-10)
        
        # Calculate stereo width preservation
        width_preservation = 1.0 - abs(orig_separation - conv_separation)
        balance_preservation = 1.0 - abs(np.log10(orig_balance) - np.log10(conv_balance)) / 2.0
        
        # Overall stereo imaging quality
        imaging_quality = (width_preservation + balance_preservation) / 2.0
        
        return {
            'separation': float(1.0 - abs(conv_separation)),
            'width_preservation': float(np.clip(width_preservation, 0.0, 1.0)),
            'balance_preservation': float(np.clip(balance_preservation, 0.0, 1.0)),
            'imaging_quality': float(np.clip(imaging_quality, 0.0, 1.0)),
            'channel_correlation': float(conv_separation)
        }
    
    async def _calculate_thd(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate Total Harmonic Distortion"""        # This is a simplified THD calculation
        # In production, use specialized audio analysis libraries
        
        # Calculate FFT
        fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
        
        # Find fundamental frequency (peak in spectrum)
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft[:len(fft)//2])
        
        # Find peak (fundamental)
        fundamental_idx = np.argmax(positive_fft)
        fundamental_freq = positive_freqs[fundamental_idx]
        fundamental_power = positive_fft[fundamental_idx]**2
        
        # Calculate harmonic powers
        harmonic_powers = []
        for harmonic in range(2, 6):  # 2nd to 5th harmonics
            harmonic_freq = fundamental_freq * harmonic
            # Find closest frequency bin
            harmonic_idx = np.argmin(np.abs(positive_freqs - harmonic_freq))
            harmonic_powers.append(positive_fft[harmonic_idx]**2)
        
        # Calculate THD
        total_harmonic_power = sum(harmonic_powers)
        thd = np.sqrt(total_harmonic_power) / np.sqrt(fundamental_power + 1e-10)
        
        return float(thd * 100)  # Return as percentage
    
    async def _calculate_imd(self,
                           original: np.ndarray,
                           converted: np.ndarray,
                           sample_rate: int) -> float:
        """Calculate Intermodulation Distortion"""        # Simplified IMD calculation
        # Calculate the difference signal
        if len(original) == len(converted):
            diff = converted - original
            # IMD is related to the energy in the difference signal
            imd = np.sqrt(np.mean(diff**2)) / (np.sqrt(np.mean(original**2)) + 1e-10)
            return float(imd * 100)
        return 0.0
    
    def _calculate_spectral_contrast_similarity(self,
                                              original: np.ndarray,
                                              converted: np.ndarray,
                                              sample_rate: int) -> float:
        """Calculate spectral contrast similarity"""        orig_contrast = librosa.feature.spectral_contrast(y=original, sr=sample_rate)
        conv_contrast = librosa.feature.spectral_contrast(y=converted, sr=sample_rate)
        
        # Ensure same shape
        min_shape = min(orig_contrast.shape[1], conv_contrast.shape[1])
        orig_contrast = orig_contrast[:, :min_shape]
        conv_contrast = conv_contrast[:, :min_shape]
        
        # Calculate similarity
        contrast_diff = np.mean(np.abs(orig_contrast - conv_contrast))
        similarity = np.exp(-contrast_diff)  # Exponential decay similarity
        
        return float(np.clip(similarity, 0.0, 1.0))
    
    async def _calculate_overall_quality_score(self,
                                             spectral: Dict[str, float],
                                             dynamic_range: Dict[str, float],
                                             frequency: Dict[str, float],
                                             noise: Dict[str, float],
                                             distortion: Dict[str, float],
                                             stereo: Dict[str, float]) -> float:
        """Calculate weighted overall quality score"""        # Define weights for different quality aspects
        weights = {
            'spectral': 0.25,
            'dynamic_range': 0.20,
            'frequency': 0.25,
            'noise': 0.15,
            'distortion': 0.10,
            'stereo': 0.05
        }
        
        # Calculate component scores
        spectral_score = spectral.get('correlation', 0.0) * 0.4 + \
                        spectral.get('centroid_similarity', 0.0) * 0.3 + \
                        spectral.get('rolloff_similarity', 0.0) * 0.3
        
        dynamic_score = dynamic_range.get('preservation', 0.0)
        frequency_score = frequency.get('accuracy', 0.0)
        noise_score = noise.get('snr_preservation', 0.0)
        distortion_score = max(0.0, 1.0 - distortion.get('distortion_level', 1.0))
        stereo_score = stereo.get('imaging_quality', 1.0) if stereo else 1.0
        
        # Calculate weighted overall score
        overall_score = (
            spectral_score * weights['spectral'] +
            dynamic_score * weights['dynamic_range'] +
            frequency_score * weights['frequency'] +
            noise_score * weights['noise'] +
            distortion_score * weights['distortion'] +
            stereo_score * weights['stereo']
        )
        
        return float(np.clip(overall_score, 0.0, 1.0))
    
    async def _assess_quality_compliance(self,
                                       metrics: Dict[str, float],
                                       quality_profile: Optional[QualityProfile]) -> str:
        """Assess quality compliance with standards"""        if not quality_profile:
            return "No quality profile specified"
        
        profile_name = quality_profile.name.lower()
        if profile_name not in self.quality_standards:
            return f"Unknown quality profile: {profile_name}"
        
        standards = self.quality_standards[profile_name]
        compliance_issues = []
        
        # Check SNR
        if metrics.get('snr_db', 0) < standards['min_snr']:
            compliance_issues.append(f"SNR below standard: {metrics.get('snr_db', 0):.1f} < {standards['min_snr']}")
        
        # Check THD
        if metrics.get('thd', 100) > standards['max_thd']:
            compliance_issues.append(f"THD above standard: {metrics.get('thd', 100):.3f}% > {standards['max_thd']}%")
        
        # Check frequency response
        if metrics.get('max_deviation_db', 100) > standards['frequency_response_tolerance']:
            compliance_issues.append(f"Frequency response deviation: {metrics.get('max_deviation_db', 100):.1f} > {standards['frequency_response_tolerance']}")
        
        if not compliance_issues:
            return f"Fully compliant with {profile_name} standards"
        else:
            return f"Compliance issues: {'; '.join(compliance_issues)}"
    
    async def _generate_compliance_report(self,
                                        metrics: Dict[str, float],
                                        quality_profile: Optional[QualityProfile]) -> Dict[str, Any]:
        """Generate detailed compliance report"""        if not quality_profile or quality_profile.name.lower() not in self.quality_standards:
            return {"status": "no_standards", "message": "No applicable quality standards"}
        
        standards = self.quality_standards[quality_profile.name.lower()]
        report = {
            "profile": quality_profile.name,
            "timestamp": datetime.now().isoformat(),
            "overall_compliance": True,
            "checks": {}
        }
        
        # Check each standard
        for standard, requirement in standards.items():
            if standard == 'min_snr':
                actual = metrics.get('snr_db', 0)
                passed = actual >= requirement
                report["checks"]["snr"] = {
                    "passed": passed,
                    "required": requirement,
                    "actual": actual,
                    "unit": "dB"
                }
                
            elif standard == 'max_thd':
                actual = metrics.get('thd', 100)
                passed = actual <= requirement
                report["checks"]["thd"] = {
                    "passed": passed,
                    "required": requirement,
                    "actual": actual,
                    "unit": "%"
                }
                
            # Add more checks...
            
            if not passed:
                report["overall_compliance"] = False
        
        return report


class QualityMetrics:
    """Quality metrics data structure"""    
    def __init__(self,
                 overall_score: float = 0.0,
                 spectral_similarity: float = 0.0,
                 dynamic_range_preservation: float = 0.0,
                 frequency_response_accuracy: float = 0.0,
                 noise_floor_level: float = 0.0,
                 distortion_level: float = 0.0,
                 stereo_imaging_quality: float = 1.0,
                 detailed_metrics: Optional[Dict[str, float]] = None,
                 quality_assessment: str = "",
                 compliance_report: Optional[Dict[str, Any]] = None,
                 error_message: Optional[str] = None):
        
        self.overall_score = overall_score
        self.spectral_similarity = spectral_similarity
        self.dynamic_range_preservation = dynamic_range_preservation
        self.frequency_response_accuracy = frequency_response_accuracy
        self.noise_floor_level = noise_floor_level
        self.distortion_level = distortion_level
        self.stereo_imaging_quality = stereo_imaging_quality
        self.detailed_metrics = detailed_metrics or {}
        self.quality_assessment = quality_assessment
        self.compliance_report = compliance_report or {}
        self.error_message = error_message


class QualityOptimizer:
    """    Intelligent Quality Optimization System
    
    Advanced optimization algorithms for maximizing audio quality
    during format conversion while meeting specific requirements.
    """    
    def __init__(self, config: QualityConfig):
        """Initialize quality optimizer"""        self.config = config
        self.optimization_history: Dict[str, List[Dict]] = {}
        
    async def optimize_conversion_parameters(self,
                                           audio_data: np.ndarray,
                                           sample_rate: int,
                                           target_format: str,
                                           quality_profile: QualityProfile) -> Dict[str, Any]:
        """        Optimize conversion parameters for maximum quality
        
        Args:
            audio_data: Input audio data
            sample_rate: Input sample rate
            target_format: Target audio format
            quality_profile: Quality requirements
            
        Returns:
            Optimized conversion parameters
        """        # Analyze audio characteristics
        audio_analysis = await self._analyze_audio_characteristics(
            audio_data, sample_rate
        )
        
        # Get format-specific optimization
        format_optimization = await self._get_format_optimization(
            target_format, audio_analysis, quality_profile
        )
        
        # Apply quality profile optimization
        profile_optimization = await self._apply_quality_profile_optimization(
            quality_profile, audio_analysis, format_optimization
        )
        
        # Combine optimizations
        optimized_params = await self._combine_optimizations(
            format_optimization, profile_optimization
        )
        
        return optimized_params
    
    async def _analyze_audio_characteristics(self,
                                           audio_data: np.ndarray,
                                           sample_rate: int) -> Dict[str, Any]:
        """Analyze audio characteristics for optimization"""        analysis = {
            'sample_rate': sample_rate,
            'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
            'duration': len(audio_data) / sample_rate,
            'bit_depth_estimate': self._estimate_bit_depth(audio_data),
            'dynamic_range': self._calculate_dynamic_range(audio_data),
            'frequency_content': await self._analyze_frequency_content(audio_data, sample_rate),
            'complexity': await self._calculate_audio_complexity(audio_data, sample_rate)
        }
        
        return analysis
    
    def _estimate_bit_depth(self, audio_data: np.ndarray) -> int:
        """Estimate effective bit depth of audio"""        # Calculate noise floor to estimate bit depth
        sorted_values = np.sort(np.abs(audio_data.flatten()))
        noise_floor = np.mean(sorted_values[:len(sorted_values)//100])  # Bottom 1%
        
        # Estimate bit depth from dynamic range
        peak_value = np.max(np.abs(audio_data))
        dynamic_range_db = 20 * np.log10(peak_value / (noise_floor + 1e-10))
        
        # Convert to approximate bit depth (6 dB per bit)
        estimated_bits = max(8, min(32, int(dynamic_range_db / 6)))
        
        return estimated_bits
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range in dB"""        rms = np.sqrt(np.mean(audio_data**2))
        peak = np.max(np.abs(audio_data))
        
        return 20 * np.log10(peak / (rms + 1e-10))
    
    async def _analyze_frequency_content(self,
                                       audio_data: np.ndarray,
                                       sample_rate: int) -> Dict[str, float]:
        """Analyze frequency content distribution"""        # Calculate spectrum
        freqs, psd = signal.welch(audio_data, fs=sample_rate, nperseg=2048)
        
        # Calculate energy in different frequency bands
        nyquist = sample_rate / 2
        
        # Define frequency bands
        bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
            'high_mid': (2000, 4000),
            'presence': (4000, 8000),
            'brilliance': (8000, nyquist)
        }
        
        band_energy = {}
        for band_name, (low_freq, high_freq) in bands.items():
            mask = (freqs >= low_freq) & (freqs <= high_freq)
            band_energy[band_name] = np.sum(psd[mask])
        
        # Calculate spectral centroid and rolloff
        centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        
        return {
            **band_energy,
            'spectral_centroid_mean': float(np.mean(centroid)),
            'spectral_rolloff_mean': float(np.mean(rolloff)),
            'bandwidth': float(rolloff.mean() - centroid.mean())
        }
    
    async def _calculate_audio_complexity(self,
                                        audio_data: np.ndarray,
                                        sample_rate: int) -> float:
        """Calculate audio complexity score for optimization"""        # Calculate spectral complexity
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        spectral_complexity = np.mean(np.var(spectral_contrast, axis=1))
        
        # Calculate temporal complexity (zero crossing rate variation)
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        temporal_complexity = np.var(zcr)
        
        # Calculate tonal complexity (chroma variation)
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        tonal_complexity = np.mean(np.var(chroma, axis=1))
        
        # Combine complexities
        overall_complexity = (spectral_complexity + temporal_complexity + tonal_complexity) / 3
        
        return float(np.clip(overall_complexity, 0.0, 1.0))
    
    async def _get_format_optimization(self,
                                     target_format: str,
                                     audio_analysis: Dict[str, Any],
                                     quality_profile: QualityProfile) -> Dict[str, Any]:
        """Get format-specific optimization parameters"""        format_optimizations = {
            'mp3': await self._optimize_mp3(audio_analysis, quality_profile),
            'aac': await self._optimize_aac(audio_analysis, quality_profile),
            'ogg': await self._optimize_ogg(audio_analysis, quality_profile),
            'flac': await self._optimize_flac(audio_analysis, quality_profile),
            'wav': await self._optimize_wav(audio_analysis, quality_profile)
        }
        
        return format_optimizations.get(target_format.lower(), {})
    
    async def _optimize_mp3(self,
                          audio_analysis: Dict[str, Any],
                          quality_profile: QualityProfile) -> Dict[str, Any]:
        """Optimize MP3 encoding parameters"""        # Base settings
        optimization = {
            'bitrate_mode': 'vbr',  # Variable bitrate for efficiency
            'quality': 2,  # High quality VBR setting
            'joint_stereo': True
        }
        
        # Adjust based on audio complexity
        complexity = audio_analysis.get('complexity', 0.5)
        if complexity > 0.7:
            optimization['quality'] = 0  # Highest quality for complex audio
        elif complexity < 0.3:
            optimization['quality'] = 4  # Lower quality for simple audio
        
        # Adjust for quality profile
        if quality_profile.name == 'archival':
            optimization.update({
                'bitrate_mode': 'cbr',
                'bitrate': 320,
                'quality': 0
            })
        elif quality_profile.name == 'streaming':
            optimization.update({
                'bitrate': 192,
                'quality': 3
            })
        
        return optimization
    
    async def _optimize_aac(self,
                          audio_analysis: Dict[str, Any],
                          quality_profile: QualityProfile) -> Dict[str, Any]:
        """Optimize AAC encoding parameters"""        optimization = {
            'bitrate': 256,
            'profile': 'aac_lc',
            'cutoff': 20000
        }
        
        # Adjust based on frequency content
        freq_content = audio_analysis.get('frequency_content', {})
        if freq_content.get('brilliance', 0) < freq_content.get('mid', 1) * 0.1:
            optimization['cutoff'] = 16000  # Lower cutoff for low-freq content
        
        return optimization
    
    async def _optimize_ogg(self,
                          audio_analysis: Dict[str, Any],
                          quality_profile: QualityProfile) -> Dict[str, Any]:
        """Optimize OGG Vorbis encoding parameters"""        optimization = {
            'quality': 6,  # High quality setting (0-10 scale)
            'managed_bitrate': False
        }
        
        if quality_profile.name == 'professional':
            optimization['quality'] = 10
        elif quality_profile.name == 'streaming':
            optimization.update({
                'quality': 4,
                'managed_bitrate': True,
                'bitrate': 192
            })
        
        return optimization
    
    async def _optimize_flac(self,
                           audio_analysis: Dict[str, Any],
                           quality_profile: QualityProfile) -> Dict[str, Any]:
        """Optimize FLAC encoding parameters"""        optimization = {
            'compression_level': 5,  # Balanced compression
            'verify': True
        }
        
        # Adjust compression based on complexity
        complexity = audio_analysis.get('complexity', 0.5)
        if complexity > 0.8:
            optimization['compression_level'] = 8  # Maximum compression
        elif complexity < 0.2:
            optimization['compression_level'] = 0  # Fast compression
        
        return optimization
    
    async def _optimize_wav(self,
                          audio_analysis: Dict[str, Any],
                          quality_profile: QualityProfile) -> Dict[str, Any]:
        """Optimize WAV format parameters"""        estimated_bits = audio_analysis.get('bit_depth_estimate', 16)
        
        optimization = {
            'bit_depth': min(32, max(16, estimated_bits)),
            'dither': True if estimated_bits < 16 else False
        }
        
        if quality_profile.name in ['professional', 'archival']:
            optimization['bit_depth'] = 32
        
        return optimization
    
    async def _apply_quality_profile_optimization(self,
                                                quality_profile: QualityProfile,
                                                audio_analysis: Dict[str, Any],
                                                format_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality profile specific optimizations"""        profile_optimizations = {
            'streaming': {
                'sample_rate_limit': 48000,
                'apply_loudness_normalization': True,
                'target_lufs': -14.0
            },
            'professional': {
                'preserve_sample_rate': True,
                'apply_dithering': True,
                'high_precision_processing': True
            },
            'archival': {
                'preserve_all_metadata': True,
                'verify_integrity': True,
                'backup_original_format': True
            },
            'broadcast': {
                'conform_to_ebu_r128': True,
                'apply_limiting': True,
                'target_lufs': -23.0
            }
        }
        
        return profile_optimizations.get(quality_profile.name, {})
    
    async def _combine_optimizations(self,
                                   format_optimization: Dict[str, Any],
                                   profile_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Combine format and profile optimizations"""        combined = {**format_optimization, **profile_optimization}
        
        # Resolve conflicts with priority to profile optimization
        return combined


# Export main classes
__all__ = [
    'QualityController',
    'QualityMetrics',
    'QualityOptimizer',
    'QualityAnalysis'
]
