"""
🎯 Audio Quality Validator - Professional Audio Validation System

Advanced audio quality validation engine for comprehensive audio content
assessment. Provides detailed quality analysis, scoring, and validation
against professional audio standards.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np
import librosa
from scipy import signal, stats
from sklearn.metrics import mean_squared_error

from .standards import QualityProfile, QualityStandards
from .metrics import QualityMetrics, QualityReport, QualityScore

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"           # Basic quality checks
    STANDARD = "standard"     # Standard professional validation
    STRICT = "strict"         # Strict validation requirements
    BROADCAST = "broadcast"   # Broadcast quality standards


class ValidationCategory(Enum):
    """Audio validation categories"""
    TECHNICAL = "technical"
    PERCEPTUAL = "perceptual"
    CONTENT = "content"
    COMPLIANCE = "compliance"
    PLATFORM = "platform"


@dataclass
class ValidationResult:
    """Individual validation result"""
    category: ValidationCategory
    test_name: str
    passed: bool
    score: float
    threshold: float
    actual_value: float
    message: str
    recommendations: List[str]
    severity: str = "info"  # info, warning, error, critical


class AudioQualityValidator:
    """
    🎯 Professional Audio Quality Validator
    
    Comprehensive audio validation system:
    - Technical quality analysis
    - Perceptual quality assessment
    - Content validation
    - Platform compliance checking
    - Professional standards enforcement
    """
    
    def __init__(self):
        self.quality_standards = QualityStandards()
        
        # Validation thresholds by level
        self.thresholds = {
            ValidationLevel.BASIC: {
                'min_sample_rate': 22050,
                'min_bit_depth': 16,
                'max_clipping': 0.01,
                'min_snr': 30,
                'max_thd': 10.0,
                'min_dynamic_range': 15
            },
            ValidationLevel.STANDARD: {
                'min_sample_rate': 44100,
                'min_bit_depth': 16,
                'max_clipping': 0.005,
                'min_snr': 40,
                'max_thd': 5.0,
                'min_dynamic_range': 25
            },
            ValidationLevel.STRICT: {
                'min_sample_rate': 44100,
                'min_bit_depth': 24,
                'max_clipping': 0.001,
                'min_snr': 50,
                'max_thd': 1.0,
                'min_dynamic_range': 35
            },
            ValidationLevel.BROADCAST: {
                'min_sample_rate': 48000,
                'min_bit_depth': 24,
                'max_clipping': 0.0001,
                'min_snr': 60,
                'max_thd': 0.1,
                'min_dynamic_range': 40
            }
        }
        
        logger.info("AudioQualityValidator initialized")
    
    async def validate_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_profile: QualityProfile,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> QualityReport:
        """
        Perform comprehensive audio validation
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate in Hz
            quality_profile: Target quality profile
            validation_level: Validation strictness level
            
        Returns:
            QualityReport with validation results
        """
        start_time = datetime.now()
        
        try:
            # Get validation thresholds
            thresholds = self.thresholds[validation_level]
            
            # Run all validation tests
            validation_results = []
            
            # Technical validation
            technical_results = await self._validate_technical_quality(
                audio_data, sample_rate, thresholds
            )
            validation_results.extend(technical_results)
            
            # Perceptual validation
            perceptual_results = await self._validate_perceptual_quality(
                audio_data, sample_rate, quality_profile
            )
            validation_results.extend(perceptual_results)
            
            # Content validation
            content_results = await self._validate_content_characteristics(
                audio_data, sample_rate, quality_profile
            )
            validation_results.extend(content_results)
            
            # Platform compliance validation
            platform_results = await self._validate_platform_compliance(
                audio_data, sample_rate, quality_profile
            )
            validation_results.extend(platform_results)
            
            # Calculate overall scores
            overall_score = self._calculate_overall_score(validation_results)
            category_scores = self._calculate_category_scores(validation_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(validation_results)
            
            # Create quality metrics
            quality_metrics = QualityMetrics(
                overall_score=overall_score,
                technical_score=category_scores.get(ValidationCategory.TECHNICAL, 0.0),
                perceptual_score=category_scores.get(ValidationCategory.PERCEPTUAL, 0.0),
                content_score=category_scores.get(ValidationCategory.CONTENT, 0.0),
                compliance_score=category_scores.get(ValidationCategory.COMPLIANCE, 0.0),
                timestamp=start_time
            )
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create quality report
            report = QualityReport(
                metrics=quality_metrics,
                validation_results=validation_results,
                recommendations=recommendations,
                overall_score=overall_score,
                processing_time=processing_time,
                validation_level=validation_level.value,
                profile_name=quality_profile.name
            )
            
            logger.info(f"Audio validation completed: score={overall_score:.3f}, "
                       f"time={processing_time:.2f}s")
            
            return report
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            raise
    
    async def _validate_technical_quality(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        thresholds: Dict[str, float]
    ) -> List[ValidationResult]:
        """Validate technical audio quality parameters"""
        results = []
        
        try:
            # Sample rate validation
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="sample_rate",
                passed=sample_rate >= thresholds['min_sample_rate'],
                score=min(1.0, sample_rate / thresholds['min_sample_rate']),
                threshold=thresholds['min_sample_rate'],
                actual_value=sample_rate,
                message=f"Sample rate: {sample_rate} Hz (min: {thresholds['min_sample_rate']} Hz)",
                recommendations=["Increase sample rate for better quality"] if sample_rate < thresholds['min_sample_rate'] else []
            ))
            
            # Clipping detection
            clipping_ratio = self._calculate_clipping_ratio(audio_data)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="clipping",
                passed=clipping_ratio <= thresholds['max_clipping'],
                score=max(0.0, 1.0 - (clipping_ratio / thresholds['max_clipping'])),
                threshold=thresholds['max_clipping'],
                actual_value=clipping_ratio,
                message=f"Clipping ratio: {clipping_ratio:.4f} (max: {thresholds['max_clipping']:.4f})",
                recommendations=["Reduce input gain to prevent clipping"] if clipping_ratio > thresholds['max_clipping'] else [],
                severity="error" if clipping_ratio > thresholds['max_clipping'] else "info"
            ))
            
            # Signal-to-noise ratio
            snr = self._calculate_snr(audio_data)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="snr",
                passed=snr >= thresholds['min_snr'],
                score=min(1.0, snr / thresholds['min_snr']),
                threshold=thresholds['min_snr'],
                actual_value=snr,
                message=f"Signal-to-noise ratio: {snr:.1f} dB (min: {thresholds['min_snr']} dB)",
                recommendations=["Apply noise reduction"] if snr < thresholds['min_snr'] else []
            ))
            
            # Total harmonic distortion
            thd = self._calculate_thd(audio_data, sample_rate)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="thd",
                passed=thd <= thresholds['max_thd'],
                score=max(0.0, 1.0 - (thd / thresholds['max_thd'])),
                threshold=thresholds['max_thd'],
                actual_value=thd,
                message=f"Total harmonic distortion: {thd:.2f}% (max: {thresholds['max_thd']:.2f}%)",
                recommendations=["Check for distortion sources"] if thd > thresholds['max_thd'] else []
            ))
            
            # Dynamic range
            dynamic_range = self._calculate_dynamic_range(audio_data)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="dynamic_range",
                passed=dynamic_range >= thresholds['min_dynamic_range'],
                score=min(1.0, dynamic_range / thresholds['min_dynamic_range']),
                threshold=thresholds['min_dynamic_range'],
                actual_value=dynamic_range,
                message=f"Dynamic range: {dynamic_range:.1f} dB (min: {thresholds['min_dynamic_range']} dB)",
                recommendations=["Reduce compression to increase dynamic range"] if dynamic_range < thresholds['min_dynamic_range'] else []
            ))
            
            # Peak level check
            peak_level = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="peak_level",
                passed=peak_level <= -0.1,  # Leave 0.1 dB headroom
                score=max(0.0, 1.0 - max(0, (peak_level + 0.1) / 6.0)),  # Penalize up to +6dB
                threshold=-0.1,
                actual_value=peak_level,
                message=f"Peak level: {peak_level:.1f} dBFS (max: -0.1 dBFS)",
                recommendations=["Reduce overall level to prevent digital clipping"] if peak_level > -0.1 else []
            ))
            
            # RMS level check
            rms_level = 20 * np.log10(np.sqrt(np.mean(audio_data ** 2)) + 1e-10)
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="rms_level",
                passed=-30 <= rms_level <= -6,  # Reasonable RMS range
                score=1.0 if -30 <= rms_level <= -6 else max(0.0, 1.0 - abs(rms_level + 18) / 18),
                threshold=-18.0,  # Target RMS level
                actual_value=rms_level,
                message=f"RMS level: {rms_level:.1f} dBFS (target: -18 dBFS)",
                recommendations=[
                    "Increase audio level" if rms_level < -30 else "Reduce audio level" if rms_level > -6 else "Good RMS level"
                ]
            ))
            
        except Exception as e:
            logger.error(f"Technical quality validation failed: {e}")
            results.append(ValidationResult(
                category=ValidationCategory.TECHNICAL,
                test_name="technical_error",
                passed=False,
                score=0.0,
                threshold=0.0,
                actual_value=0.0,
                message=f"Technical validation error: {str(e)}",
                recommendations=["Check audio file integrity"],
                severity="error"
            ))
        
        return results
    
    async def _validate_perceptual_quality(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_profile: QualityProfile
    ) -> List[ValidationResult]:
        """Validate perceptual audio quality aspects"""
        results = []
        
        try:
            # Frequency response analysis
            freq_balance_score = self._analyze_frequency_balance(audio_data, sample_rate)
            results.append(ValidationResult(
                category=ValidationCategory.PERCEPTUAL,
                test_name="frequency_balance",
                passed=freq_balance_score >= 0.7,
                score=freq_balance_score,
                threshold=0.7,
                actual_value=freq_balance_score,
                message=f"Frequency balance score: {freq_balance_score:.3f}",
                recommendations=["Apply EQ to improve frequency balance"] if freq_balance_score < 0.7 else []
            ))
            
            # Loudness analysis
            loudness_score = self._analyze_loudness_quality(audio_data, sample_rate)
            results.append(ValidationResult(
                category=ValidationCategory.PERCEPTUAL,
                test_name="loudness_quality",
                passed=loudness_score >= 0.6,
                score=loudness_score,
                threshold=0.6,
                actual_value=loudness_score,
                message=f"Loudness quality score: {loudness_score:.3f}",
                recommendations=["Adjust loudness processing"] if loudness_score < 0.6 else []
            ))
            
            # Stereo imaging (if stereo)
            if audio_data.ndim > 1 or len(audio_data.shape) > 1:
                stereo_score = self._analyze_stereo_imaging(audio_data)
                results.append(ValidationResult(
                    category=ValidationCategory.PERCEPTUAL,
                    test_name="stereo_imaging",
                    passed=stereo_score >= 0.5,
                    score=stereo_score,
                    threshold=0.5,
                    actual_value=stereo_score,
                    message=f"Stereo imaging score: {stereo_score:.3f}",
                    recommendations=["Improve stereo width"] if stereo_score < 0.5 else []
                ))
            
            # Temporal consistency
            temporal_score = self._analyze_temporal_consistency(audio_data, sample_rate)
            results.append(ValidationResult(
                category=ValidationCategory.PERCEPTUAL,
                test_name="temporal_consistency",
                passed=temporal_score >= 0.7,
                score=temporal_score,
                threshold=0.7,
                actual_value=temporal_score,
                message=f"Temporal consistency score: {temporal_score:.3f}",
                recommendations=["Check for audio artifacts"] if temporal_score < 0.7 else []
            ))
            
        except Exception as e:
            logger.error(f"Perceptual quality validation failed: {e}")
            results.append(ValidationResult(
                category=ValidationCategory.PERCEPTUAL,
                test_name="perceptual_error",
                passed=False,
                score=0.0,
                threshold=0.0,
                actual_value=0.0,
                message=f"Perceptual validation error: {str(e)}",
                recommendations=["Check perceptual quality manually"],
                severity="error"
            ))
        
        return results
    
    async def _validate_content_characteristics(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_profile: QualityProfile
    ) -> List[ValidationResult]:
        """Validate content-specific characteristics"""
        results = []
        
        try:
            # Duration validation
            duration = len(audio_data) / sample_rate
            min_duration = quality_profile.requirements.get('min_duration', 1.0)
            max_duration = quality_profile.requirements.get('max_duration', 600.0)
            
            duration_valid = min_duration <= duration <= max_duration
            results.append(ValidationResult(
                category=ValidationCategory.CONTENT,
                test_name="duration",
                passed=duration_valid,
                score=1.0 if duration_valid else 0.5,
                threshold=min_duration,
                actual_value=duration,
                message=f"Duration: {duration:.1f}s (range: {min_duration}-{max_duration}s)",
                recommendations=["Adjust audio duration"] if not duration_valid else []
            ))
            
            # Silence analysis
            silence_ratio = self._calculate_silence_ratio(audio_data)
            max_silence = quality_profile.requirements.get('max_silence_ratio', 0.3)
            
            results.append(ValidationResult(
                category=ValidationCategory.CONTENT,
                test_name="silence_ratio",
                passed=silence_ratio <= max_silence,
                score=max(0.0, 1.0 - (silence_ratio / max_silence)),
                threshold=max_silence,
                actual_value=silence_ratio,
                message=f"Silence ratio: {silence_ratio:.3f} (max: {max_silence:.3f})",
                recommendations=["Reduce silent portions"] if silence_ratio > max_silence else []
            ))
            
            # Content type detection
            content_type = self._detect_content_type(audio_data, sample_rate)
            expected_type = quality_profile.content_type
            
            type_match = content_type == expected_type or expected_type == "any"
            results.append(ValidationResult(
                category=ValidationCategory.CONTENT,
                test_name="content_type",
                passed=type_match,
                score=1.0 if type_match else 0.7,
                threshold=0.0,
                actual_value=0.0,
                message=f"Detected: {content_type}, Expected: {expected_type}",
                recommendations=[] if type_match else [f"Content appears to be {content_type}, not {expected_type}"]
            ))
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            results.append(ValidationResult(
                category=ValidationCategory.CONTENT,
                test_name="content_error",
                passed=False,
                score=0.0,
                threshold=0.0,
                actual_value=0.0,
                message=f"Content validation error: {str(e)}",
                recommendations=["Check audio content manually"],
                severity="error"
            ))
        
        return results
    
    async def _validate_platform_compliance(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_profile: QualityProfile
    ) -> List[ValidationResult]:
        """Validate platform-specific compliance requirements"""
        results = []
        
        try:
            # Platform-specific requirements from profile
            platform_requirements = quality_profile.platform_requirements
            
            for requirement, value in platform_requirements.items():
                if requirement == "max_file_size":
                    # Estimate file size (assuming 16-bit WAV)
                    estimated_size = len(audio_data) * 2  # 2 bytes per sample
                    passed = estimated_size <= value
                    results.append(ValidationResult(
                        category=ValidationCategory.COMPLIANCE,
                        test_name=f"platform_{requirement}",
                        passed=passed,
                        score=1.0 if passed else 0.0,
                        threshold=value,
                        actual_value=estimated_size,
                        message=f"Estimated size: {estimated_size} bytes (max: {value} bytes)",
                        recommendations=["Compress audio to reduce file size"] if not passed else []
                    ))
                
                elif requirement == "required_sample_rates":
                    # Check if sample rate is in required list
                    passed = sample_rate in value
                    results.append(ValidationResult(
                        category=ValidationCategory.COMPLIANCE,
                        test_name=f"platform_{requirement}",
                        passed=passed,
                        score=1.0 if passed else 0.5,
                        threshold=0.0,
                        actual_value=sample_rate,
                        message=f"Sample rate: {sample_rate} Hz, Required: {value}",
                        recommendations=[f"Convert to one of: {value}"] if not passed else []
                    ))
                
                elif requirement == "max_channels":
                    channels = 1 if audio_data.ndim == 1 else audio_data.shape[0]
                    passed = channels <= value
                    results.append(ValidationResult(
                        category=ValidationCategory.COMPLIANCE,
                        test_name=f"platform_{requirement}",
                        passed=passed,
                        score=1.0 if passed else 0.0,
                        threshold=value,
                        actual_value=channels,
                        message=f"Channels: {channels} (max: {value})",
                        recommendations=["Convert to mono or stereo"] if not passed else []
                    ))
            
        except Exception as e:
            logger.error(f"Platform compliance validation failed: {e}")
            results.append(ValidationResult(
                category=ValidationCategory.COMPLIANCE,
                test_name="compliance_error",
                passed=False,
                score=0.0,
                threshold=0.0,
                actual_value=0.0,
                message=f"Compliance validation error: {str(e)}",
                recommendations=["Check platform requirements manually"],
                severity="error"
            ))
        
        return results
    
    def _calculate_clipping_ratio(self, audio_data: np.ndarray, threshold: float = 0.99) -> float:
        """Calculate ratio of clipped samples"""
        clipped_samples = np.sum(np.abs(audio_data) >= threshold)
        return clipped_samples / len(audio_data)
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        # Simple SNR estimation using signal power vs noise floor
        signal_power = np.mean(audio_data ** 2)
        
        # Estimate noise as difference from median filtered signal
        noise_estimate = audio_data - signal.medfilt(audio_data, kernel_size=3)
        noise_power = np.mean(noise_estimate ** 2)
        
        if noise_power < 1e-10:
            return 100.0  # Very high SNR
        
        snr_linear = signal_power / noise_power
        return 10 * np.log10(snr_linear + 1e-10)
    
    def _calculate_thd(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate total harmonic distortion"""
        # Find dominant frequency
        fft = np.fft.fft(audio_data[:min(len(audio_data), sample_rate)])  # Use 1 second max
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        
        # Get magnitude spectrum
        magnitude = np.abs(fft)
        
        # Find fundamental frequency (highest peak)
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        if len(positive_magnitude) == 0:
            return 0.0
        
        fundamental_idx = np.argmax(positive_magnitude[10:]) + 10  # Skip DC
        fundamental_freq = positive_freqs[fundamental_idx]
        fundamental_amplitude = positive_magnitude[fundamental_idx]
        
        if fundamental_freq < 20 or fundamental_amplitude == 0:
            return 0.0
        
        # Find harmonics
        harmonic_power = 0
        for harmonic in range(2, 6):  # 2nd to 5th harmonic
            harmonic_freq = fundamental_freq * harmonic
            if harmonic_freq >= sample_rate / 2:
                break
            
            # Find closest frequency bin
            harmonic_idx = np.argmin(np.abs(positive_freqs - harmonic_freq))
            if np.abs(positive_freqs[harmonic_idx] - harmonic_freq) < fundamental_freq * 0.1:
                harmonic_power += positive_magnitude[harmonic_idx] ** 2
        
        # Calculate THD
        fundamental_power = fundamental_amplitude ** 2
        thd = np.sqrt(harmonic_power) / fundamental_amplitude * 100
        
        return min(thd, 100.0)  # Cap at 100%
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range"""
        if len(audio_data) == 0:
            return 0.0
        
        # Calculate RMS in overlapping windows
        window_size = min(len(audio_data) // 10, 4096)
        if window_size < 100:
            return 20 * np.log10(np.max(np.abs(audio_data)) / (np.mean(np.abs(audio_data)) + 1e-10))
        
        rms_values = []
        for i in range(0, len(audio_data) - window_size, window_size // 2):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms > 1e-10:
                rms_values.append(rms)
        
        if len(rms_values) < 2:
            return 0.0
        
        rms_values = np.array(rms_values)
        max_rms = np.max(rms_values)
        min_rms = np.min(rms_values[rms_values > 1e-10])  # Exclude silence
        
        dynamic_range = 20 * np.log10(max_rms / (min_rms + 1e-10))
        return min(dynamic_range, 120.0)  # Cap at 120 dB
    
    def _analyze_frequency_balance(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Analyze frequency balance quality"""
        # Calculate spectral centroid and spread
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        
        # Ideal spectral centroid range for balanced audio
        ideal_centroid = sample_rate * 0.1  # Around 4.4 kHz for 44.1 kHz
        centroid_score = 1.0 - min(1.0, abs(np.mean(spectral_centroids) - ideal_centroid) / ideal_centroid)
        
        # Frequency distribution analysis
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft[:len(fft)//2])
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)[:len(fft)//2]
        
        # Divide into frequency bands
        low_band = magnitude[(freqs >= 20) & (freqs < 250)]
        mid_band = magnitude[(freqs >= 250) & (freqs < 4000)]
        high_band = magnitude[(freqs >= 4000) & (freqs < sample_rate/2)]
        
        # Calculate band powers
        low_power = np.sum(low_band ** 2) if len(low_band) > 0 else 0
        mid_power = np.sum(mid_band ** 2) if len(mid_band) > 0 else 0
        high_power = np.sum(high_band ** 2) if len(high_band) > 0 else 0
        
        total_power = low_power + mid_power + high_power
        
        if total_power == 0:
            return 0.0
        
        # Balance score based on deviation from ideal distribution
        low_ratio = low_power / total_power
        mid_ratio = mid_power / total_power
        high_ratio = high_power / total_power
        
        # Ideal ratios (adjustable)
        ideal_low = 0.3
        ideal_mid = 0.5
        ideal_high = 0.2
        
        balance_score = 1.0 - (
            abs(low_ratio - ideal_low) + 
            abs(mid_ratio - ideal_mid) + 
            abs(high_ratio - ideal_high)
        ) / 2.0
        
        return max(0.0, (centroid_score + balance_score) / 2.0)
    
    def _analyze_loudness_quality(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Analyze loudness quality"""
        # Calculate LUFS-style loudness
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sample_rate)
            loudness = meter.integrated_loudness(audio_data)
            
            # Target loudness range: -23 to -16 LUFS
            target_min = -23
            target_max = -16
            
            if target_min <= loudness <= target_max:
                score = 1.0
            elif loudness < target_min:
                score = max(0.0, 1.0 - (target_min - loudness) / 10)
            else:
                score = max(0.0, 1.0 - (loudness - target_max) / 10)
            
            return score
            
        except ImportError:
            # Fallback to RMS-based loudness
            rms = np.sqrt(np.mean(audio_data ** 2))
            rms_db = 20 * np.log10(rms + 1e-10)
            
            # Target RMS range: -20 to -12 dB
            if -20 <= rms_db <= -12:
                return 1.0
            elif rms_db < -20:
                return max(0.0, 1.0 - (-20 - rms_db) / 20)
            else:
                return max(0.0, 1.0 - (rms_db + 12) / 20)
    
    def _analyze_stereo_imaging(self, audio_data: np.ndarray) -> float:
        """Analyze stereo imaging quality"""
        if audio_data.ndim == 1:
            return 1.0  # Mono audio, no stereo issues
        
        if audio_data.shape[0] < 2:
            return 1.0
        
        left = audio_data[0]
        right = audio_data[1]
        
        # Calculate correlation
        correlation = np.corrcoef(left, right)[0, 1]
        
        # Calculate stereo width
        mid = (left + right) / 2
        side = (left - right) / 2
        
        mid_power = np.mean(mid ** 2)
        side_power = np.mean(side ** 2)
        
        if mid_power + side_power == 0:
            return 0.5
        
        stereo_width = side_power / (mid_power + side_power + 1e-10)
        
        # Good stereo should have moderate correlation and width
        correlation_score = 1.0 - min(1.0, abs(correlation - 0.3) / 0.7)  # Target ~0.3 correlation
        width_score = 1.0 - abs(stereo_width - 0.3)  # Target ~0.3 width
        
        return (correlation_score + width_score) / 2.0
    
    def _analyze_temporal_consistency(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Analyze temporal consistency"""
        # Calculate RMS in overlapping windows
        window_size = min(len(audio_data) // 20, sample_rate // 4)  # 250ms windows max
        if window_size < 100:
            return 1.0
        
        rms_values = []
        for i in range(0, len(audio_data) - window_size, window_size // 2):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            rms_values.append(rms)
        
        if len(rms_values) < 3:
            return 1.0
        
        rms_values = np.array(rms_values)
        
        # Calculate consistency metrics
        rms_std = np.std(rms_values)
        rms_mean = np.mean(rms_values)
        
        if rms_mean == 0:
            return 0.0
        
        # Coefficient of variation
        cv = rms_std / (rms_mean + 1e-10)
        
        # Good consistency should have low variation
        consistency_score = max(0.0, 1.0 - cv)
        
        return consistency_score
    
    def _calculate_silence_ratio(self, audio_data: np.ndarray, threshold: float = 0.001) -> float:
        """Calculate ratio of silent samples"""
        silent_samples = np.sum(np.abs(audio_data) < threshold)
        return silent_samples / len(audio_data)
    
    def _detect_content_type(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Detect audio content type"""
        # Basic content type detection based on spectral characteristics
        
        # Calculate spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Simple classification rules
        if zero_crossing_rate > 0.1 and spectral_centroid > sample_rate * 0.15:
            return "speech"
        elif spectral_bandwidth > sample_rate * 0.2:
            return "music"
        elif spectral_centroid < sample_rate * 0.05:
            return "bass_heavy"
        else:
            return "general_audio"
    
    def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> float:
        """Calculate overall validation score"""
        if not validation_results:
            return 0.0
        
        # Weight different categories
        category_weights = {
            ValidationCategory.TECHNICAL: 0.35,
            ValidationCategory.PERCEPTUAL: 0.30,
            ValidationCategory.CONTENT: 0.20,
            ValidationCategory.COMPLIANCE: 0.15
        }
        
        category_scores = self._calculate_category_scores(validation_results)
        
        overall_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = category_weights.get(category, 0.25)
            overall_score += score * weight
            total_weight += weight
        
        return overall_score / max(total_weight, 1.0)
    
    def _calculate_category_scores(self, validation_results: List[ValidationResult]) -> Dict[ValidationCategory, float]:
        """Calculate scores by category"""
        category_scores = {}
        category_counts = {}
        
        for result in validation_results:
            category = result.category
            if category not in category_scores:
                category_scores[category] = 0.0
                category_counts[category] = 0
            
            category_scores[category] += result.score
            category_counts[category] += 1
        
        # Average scores within categories
        for category in category_scores:
            if category_counts[category] > 0:
                category_scores[category] /= category_counts[category]
        
        return category_scores
    
    def _generate_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Collect all recommendations from failed tests
        for result in validation_results:
            if not result.passed and result.recommendations:
                recommendations.extend(result.recommendations)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        # Add general recommendations based on common issues
        failed_tests = [r.test_name for r in validation_results if not r.passed]
        
        if "clipping" in failed_tests:
            unique_recommendations.insert(0, "CRITICAL: Fix audio clipping before proceeding")
        
        if "snr" in failed_tests:
            unique_recommendations.append("Consider noise reduction processing")
        
        if "frequency_balance" in failed_tests:
            unique_recommendations.append("Apply equalization to improve frequency response")
        
        return unique_recommendations[:10]  # Limit to top 10 recommendations
