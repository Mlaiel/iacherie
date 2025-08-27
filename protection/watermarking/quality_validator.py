"""
Watermark Quality Assessment and Validation System
Professional quality assurance for digital watermarking operations

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This watermark quality assessment system, concept, and all associated code are the exclusive 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, modification, or 
distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import statistics
from pathlib import Path

try:
    import librosa
    import soundfile as sf
    from PIL import Image
    import cv2
    from scipy import signal, stats
    from scipy.fft import fft, ifft
    import skimage.metrics
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Quality assessment metrics"""
    SNR = "signal_to_noise_ratio"
    PSNR = "peak_signal_to_noise_ratio"
    SSIM = "structural_similarity_index"
    MSE = "mean_squared_error"
    THD = "total_harmonic_distortion"
    PESQ = "perceptual_evaluation_speech_quality"
    MOS = "mean_opinion_score"
    IMPERCEPTIBILITY = "imperceptibility_score"
    ROBUSTNESS = "robustness_score"
    CAPACITY = "embedding_capacity"
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"


class QualityThreshold(Enum):
    """Quality threshold levels"""
    EXCELLENT = "excellent"      # >95% quality retention
    GOOD = "good"               # 85-95% quality retention  
    ACCEPTABLE = "acceptable"   # 70-85% quality retention
    POOR = "poor"              # 50-70% quality retention
    UNACCEPTABLE = "unacceptable"  # <50% quality retention


class ValidationStatus(Enum):
    """Validation status codes"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class QualityScore:
    """Individual quality score"""
    metric: QualityMetric
    value: float
    max_value: float
    threshold: float
    normalized_score: float  # 0-1 scale
    status: ValidationStatus
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric': self.metric.value,
            'value': self.value,
            'max_value': self.max_value,
            'threshold': self.threshold,
            'normalized_score': self.normalized_score,
            'status': self.status.value,
            'notes': self.notes
        }


@dataclass
class QualityAssessmentResult:
    """Complete quality assessment result"""
    content_type: str
    assessment_timestamp: datetime
    overall_score: float
    overall_status: ValidationStatus
    individual_scores: List[QualityScore]
    recommendations: List[str]
    processing_time_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_type': self.content_type,
            'assessment_timestamp': self.assessment_timestamp.isoformat(),
            'overall_score': self.overall_score,
            'overall_status': self.overall_status.value,
            'individual_scores': [score.to_dict() for score in self.individual_scores],
            'recommendations': self.recommendations,
            'processing_time_seconds': self.processing_time_seconds
        }
    
    def get_metric_score(self, metric: QualityMetric) -> Optional[QualityScore]:
        """Get score for specific metric"""
        for score in self.individual_scores:
            if score.metric == metric:
                return score
        return None
    
    def get_failed_metrics(self) -> List[QualityScore]:
        """Get metrics that failed validation"""
        return [score for score in self.individual_scores if score.status == ValidationStatus.FAILED]


class AudioQualityAssessor:
    """Professional audio quality assessment"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Quality thresholds
        self.thresholds = {
            QualityMetric.SNR: {'excellent': 40, 'good': 30, 'acceptable': 20, 'poor': 10},
            QualityMetric.THD: {'excellent': 0.5, 'good': 1.0, 'acceptable': 2.0, 'poor': 5.0},
            QualityMetric.IMPERCEPTIBILITY: {'excellent': 0.95, 'good': 0.85, 'acceptable': 0.70, 'poor': 0.50}
        }
    
    async def assess_audio_quality(self, 
                                 original_audio: np.ndarray,
                                 watermarked_audio: np.ndarray) -> QualityAssessmentResult:
        """Comprehensive audio quality assessment"""
        start_time = datetime.now()
        
        try:
            if not MULTIMEDIA_AVAILABLE:
                raise ValueError("Audio libraries not available")
            
            # Ensure same length
            min_len = min(len(original_audio), len(watermarked_audio))
            original = original_audio[:min_len]
            watermarked = watermarked_audio[:min_len]
            
            scores = []
            recommendations = []
            
            # 1. Signal-to-Noise Ratio
            snr_score = await self._calculate_snr(original, watermarked)
            scores.append(snr_score)
            
            # 2. Total Harmonic Distortion
            thd_score = await self._calculate_thd(original, watermarked)
            scores.append(thd_score)
            
            # 3. Spectral Distortion
            spectral_score = await self._calculate_spectral_distortion(original, watermarked)
            scores.append(spectral_score)
            
            # 4. Perceptual Quality
            perceptual_score = await self._calculate_perceptual_quality(original, watermarked)
            scores.append(perceptual_score)
            
            # 5. Dynamic Range
            dynamic_score = await self._calculate_dynamic_range_preservation(original, watermarked)
            scores.append(dynamic_score)
            
            # Calculate overall score
            valid_scores = [s.normalized_score for s in scores if s.normalized_score >= 0]
            overall_score = statistics.mean(valid_scores) if valid_scores else 0.0
            
            # Determine overall status
            overall_status = self._determine_overall_status(scores)
            
            # Generate recommendations
            recommendations = self._generate_audio_recommendations(scores)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QualityAssessmentResult(
                content_type="audio",
                assessment_timestamp=start_time,
                overall_score=overall_score,
                overall_status=overall_status,
                individual_scores=scores,
                recommendations=recommendations,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in audio quality assessment: {e}")
            raise
    
    async def _calculate_snr(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate Signal-to-Noise Ratio"""
        try:
            noise = watermarked - original
            signal_power = np.mean(original ** 2)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 100.0  # Perfect quality
            
            # Normalize score (0-1)
            normalized_score = min(max(snr_db / 50.0, 0), 1)
            
            # Determine status
            if snr_db >= self.thresholds[QualityMetric.SNR]['excellent']:
                status = ValidationStatus.PASSED
            elif snr_db >= self.thresholds[QualityMetric.SNR]['acceptable']:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.SNR,
                value=snr_db,
                max_value=100.0,
                threshold=self.thresholds[QualityMetric.SNR]['acceptable'],
                normalized_score=normalized_score,
                status=status,
                notes=f"SNR: {snr_db:.2f} dB"
            )
            
        except Exception as e:
            logger.error(f"Error calculating SNR: {e}")
            return QualityScore(
                metric=QualityMetric.SNR,
                value=0.0,
                max_value=100.0,
                threshold=20.0,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_thd(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate Total Harmonic Distortion"""
        try:
            # Simplified THD calculation
            noise = watermarked - original
            signal_rms = np.sqrt(np.mean(original ** 2))
            noise_rms = np.sqrt(np.mean(noise ** 2))
            
            if signal_rms > 0:
                thd_percent = (noise_rms / signal_rms) * 100
            else:
                thd_percent = 100.0
            
            # Normalize score (lower THD is better)
            normalized_score = max(0, 1 - (thd_percent / 10.0))
            
            # Determine status
            if thd_percent <= self.thresholds[QualityMetric.THD]['excellent']:
                status = ValidationStatus.PASSED
            elif thd_percent <= self.thresholds[QualityMetric.THD]['acceptable']:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.THD,
                value=thd_percent,
                max_value=10.0,
                threshold=self.thresholds[QualityMetric.THD]['acceptable'],
                normalized_score=normalized_score,
                status=status,
                notes=f"THD: {thd_percent:.3f}%"
            )
            
        except Exception as e:
            logger.error(f"Error calculating THD: {e}")
            return QualityScore(
                metric=QualityMetric.THD,
                value=100.0,
                max_value=10.0,
                threshold=2.0,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_spectral_distortion(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate spectral distortion"""
        try:
            # FFT analysis
            original_fft = np.abs(fft(original))
            watermarked_fft = np.abs(fft(watermarked))
            
            # Spectral distortion measure
            spectral_diff = np.mean((original_fft - watermarked_fft) ** 2)
            spectral_energy = np.mean(original_fft ** 2)
            
            if spectral_energy > 0:
                distortion_ratio = spectral_diff / spectral_energy
            else:
                distortion_ratio = 1.0
            
            # Convert to dB
            if distortion_ratio > 0:
                distortion_db = 10 * np.log10(distortion_ratio)
            else:
                distortion_db = -100.0
            
            # Normalize score (lower distortion is better)
            normalized_score = max(0, min(1, 1 + distortion_db / 50.0))
            
            # Status determination
            if distortion_db <= -30:
                status = ValidationStatus.PASSED
            elif distortion_db <= -20:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.MSE,  # Using MSE as proxy for spectral distortion
                value=distortion_db,
                max_value=0.0,
                threshold=-20.0,
                normalized_score=normalized_score,
                status=status,
                notes=f"Spectral distortion: {distortion_db:.2f} dB"
            )
            
        except Exception as e:
            logger.error(f"Error calculating spectral distortion: {e}")
            return QualityScore(
                metric=QualityMetric.MSE,
                value=0.0,
                max_value=0.0,
                threshold=-20.0,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_perceptual_quality(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate perceptual audio quality"""
        try:
            # Simplified perceptual model based on psychoacoustics
            
            # STFT for frequency analysis
            original_stft = librosa.stft(original)
            watermarked_stft = librosa.stft(watermarked)
            
            original_mag = np.abs(original_stft)
            watermarked_mag = np.abs(watermarked_stft)
            
            # Perceptual weighting (emphasize mid frequencies)
            freqs = librosa.fft_frequencies(sr=self.sample_rate)
            weights = np.ones_like(freqs)
            
            # Weight important frequency ranges more heavily
            for i, freq in enumerate(freqs):
                if 300 <= freq <= 3400:  # Speech range
                    weights[i] = 2.0
                elif 1000 <= freq <= 5000:  # Most sensitive hearing range
                    weights[i] = 3.0
            
            # Calculate weighted difference
            weighted_diff = np.mean(weights[:, np.newaxis] * (original_mag - watermarked_mag) ** 2)
            weighted_energy = np.mean(weights[:, np.newaxis] * original_mag ** 2)
            
            if weighted_energy > 0:
                perceptual_distortion = weighted_diff / weighted_energy
            else:
                perceptual_distortion = 1.0
            
            # Convert to perceptual score (0-1, higher is better)
            perceptual_score = max(0, 1 - perceptual_distortion * 10)
            
            # Status determination
            if perceptual_score >= 0.95:
                status = ValidationStatus.PASSED
            elif perceptual_score >= 0.80:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.IMPERCEPTIBILITY,
                value=perceptual_score,
                max_value=1.0,
                threshold=0.80,
                normalized_score=perceptual_score,
                status=status,
                notes=f"Perceptual quality: {perceptual_score:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating perceptual quality: {e}")
            return QualityScore(
                metric=QualityMetric.IMPERCEPTIBILITY,
                value=0.0,
                max_value=1.0,
                threshold=0.80,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_dynamic_range_preservation(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate dynamic range preservation"""
        try:
            # Calculate RMS in overlapping windows
            window_size = int(0.1 * self.sample_rate)  # 100ms windows
            hop_size = window_size // 2
            
            original_rms = []
            watermarked_rms = []
            
            for i in range(0, len(original) - window_size, hop_size):
                orig_window = original[i:i+window_size]
                water_window = watermarked[i:i+window_size]
                
                original_rms.append(np.sqrt(np.mean(orig_window ** 2)))
                watermarked_rms.append(np.sqrt(np.mean(water_window ** 2)))
            
            original_rms = np.array(original_rms)
            watermarked_rms = np.array(watermarked_rms)
            
            # Calculate dynamic range correlation
            if len(original_rms) > 1 and np.std(original_rms) > 0:
                correlation = np.corrcoef(original_rms, watermarked_rms)[0, 1]
                if np.isnan(correlation):
                    correlation = 0.0
            else:
                correlation = 1.0  # No dynamics to preserve
            
            # Normalize to 0-1
            normalized_score = max(0, correlation)
            
            # Status determination
            if correlation >= 0.95:
                status = ValidationStatus.PASSED
            elif correlation >= 0.85:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.ROBUSTNESS,  # Using as proxy for dynamic range
                value=correlation,
                max_value=1.0,
                threshold=0.85,
                normalized_score=normalized_score,
                status=status,
                notes=f"Dynamic range correlation: {correlation:.3f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating dynamic range preservation: {e}")
            return QualityScore(
                metric=QualityMetric.ROBUSTNESS,
                value=0.0,
                max_value=1.0,
                threshold=0.85,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    def _determine_overall_status(self, scores: List[QualityScore]) -> ValidationStatus:
        """Determine overall validation status"""
        failed_count = sum(1 for score in scores if score.status == ValidationStatus.FAILED)
        warning_count = sum(1 for score in scores if score.status == ValidationStatus.WARNING)
        error_count = sum(1 for score in scores if score.status == ValidationStatus.ERROR)
        
        if error_count > 0:
            return ValidationStatus.ERROR
        elif failed_count > 0:
            return ValidationStatus.FAILED
        elif warning_count > 0:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.PASSED
    
    def _generate_audio_recommendations(self, scores: List[QualityScore]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        for score in scores:
            if score.status == ValidationStatus.FAILED:
                if score.metric == QualityMetric.SNR:
                    recommendations.append("Reduce watermark embedding strength to improve SNR")
                elif score.metric == QualityMetric.THD:
                    recommendations.append("Use different embedding technique to reduce harmonic distortion")
                elif score.metric == QualityMetric.IMPERCEPTIBILITY:
                    recommendations.append("Apply perceptual masking model to improve imperceptibility")
                elif score.metric == QualityMetric.ROBUSTNESS:
                    recommendations.append("Preserve dynamic range by adjusting embedding parameters")
            
            elif score.status == ValidationStatus.WARNING:
                if score.metric == QualityMetric.SNR:
                    recommendations.append("Consider slight reduction in embedding strength")
                elif score.metric == QualityMetric.IMPERCEPTIBILITY:
                    recommendations.append("Apply adaptive embedding based on signal characteristics")
        
        if not recommendations:
            recommendations.append("Audio quality is excellent - no improvements needed")
        
        return recommendations


class ImageQualityAssessor:
    """Professional image quality assessment"""
    
    def __init__(self):
        self.thresholds = {
            QualityMetric.PSNR: {'excellent': 40, 'good': 35, 'acceptable': 30, 'poor': 25},
            QualityMetric.SSIM: {'excellent': 0.95, 'good': 0.90, 'acceptable': 0.85, 'poor': 0.75},
            QualityMetric.MSE: {'excellent': 10, 'good': 50, 'acceptable': 100, 'poor': 500}
        }
    
    async def assess_image_quality(self, 
                                 original_image: np.ndarray,
                                 watermarked_image: np.ndarray) -> QualityAssessmentResult:
        """Comprehensive image quality assessment"""
        start_time = datetime.now()
        
        try:
            if not MULTIMEDIA_AVAILABLE:
                raise ValueError("Image processing libraries not available")
            
            scores = []
            recommendations = []
            
            # 1. Peak Signal-to-Noise Ratio
            psnr_score = await self._calculate_psnr(original_image, watermarked_image)
            scores.append(psnr_score)
            
            # 2. Structural Similarity Index
            ssim_score = await self._calculate_ssim(original_image, watermarked_image)
            scores.append(ssim_score)
            
            # 3. Mean Squared Error
            mse_score = await self._calculate_mse(original_image, watermarked_image)
            scores.append(mse_score)
            
            # 4. Visual Quality Score
            visual_score = await self._calculate_visual_quality(original_image, watermarked_image)
            scores.append(visual_score)
            
            # 5. Color Fidelity
            color_score = await self._calculate_color_fidelity(original_image, watermarked_image)
            scores.append(color_score)
            
            # Calculate overall score
            valid_scores = [s.normalized_score for s in scores if s.normalized_score >= 0]
            overall_score = statistics.mean(valid_scores) if valid_scores else 0.0
            
            # Determine overall status
            overall_status = self._determine_overall_status(scores)
            
            # Generate recommendations
            recommendations = self._generate_image_recommendations(scores)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QualityAssessmentResult(
                content_type="image",
                assessment_timestamp=start_time,
                overall_score=overall_score,
                overall_status=overall_status,
                individual_scores=scores,
                recommendations=recommendations,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in image quality assessment: {e}")
            raise
    
    async def _calculate_psnr(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate Peak Signal-to-Noise Ratio"""
        try:
            mse = np.mean((original.astype(float) - watermarked.astype(float)) ** 2)
            
            if mse == 0:
                psnr_value = 100.0  # Perfect quality
            else:
                max_pixel = 255.0
                psnr_value = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            # Normalize score
            normalized_score = min(max(psnr_value / 50.0, 0), 1)
            
            # Determine status
            if psnr_value >= self.thresholds[QualityMetric.PSNR]['excellent']:
                status = ValidationStatus.PASSED
            elif psnr_value >= self.thresholds[QualityMetric.PSNR]['acceptable']:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.PSNR,
                value=psnr_value,
                max_value=100.0,
                threshold=self.thresholds[QualityMetric.PSNR]['acceptable'],
                normalized_score=normalized_score,
                status=status,
                notes=f"PSNR: {psnr_value:.2f} dB"
            )
            
        except Exception as e:
            logger.error(f"Error calculating PSNR: {e}")
            return QualityScore(
                metric=QualityMetric.PSNR,
                value=0.0,
                max_value=100.0,
                threshold=30.0,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_ssim(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate Structural Similarity Index"""
        try:
            # Convert to grayscale if needed
            if len(original.shape) == 3:
                original_gray = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)
                watermarked_gray = cv2.cvtColor(watermarked, cv2.COLOR_RGB2GRAY)
            else:
                original_gray = original
                watermarked_gray = watermarked
            
            # Calculate SSIM
            ssim_value = skimage.metrics.structural_similarity(
                original_gray, watermarked_gray, data_range=255
            )
            
            # Normalize score (SSIM is already 0-1)
            normalized_score = max(0, ssim_value)
            
            # Determine status
            if ssim_value >= self.thresholds[QualityMetric.SSIM]['excellent']:
                status = ValidationStatus.PASSED
            elif ssim_value >= self.thresholds[QualityMetric.SSIM]['acceptable']:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.SSIM,
                value=ssim_value,
                max_value=1.0,
                threshold=self.thresholds[QualityMetric.SSIM]['acceptable'],
                normalized_score=normalized_score,
                status=status,
                notes=f"SSIM: {ssim_value:.4f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating SSIM: {e}")
            return QualityScore(
                metric=QualityMetric.SSIM,
                value=0.0,
                max_value=1.0,
                threshold=0.85,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_mse(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate Mean Squared Error"""
        try:
            mse_value = np.mean((original.astype(float) - watermarked.astype(float)) ** 2)
            
            # Normalize score (lower MSE is better)
            normalized_score = max(0, 1 - (mse_value / 1000.0))
            
            # Determine status (lower MSE is better)
            if mse_value <= self.thresholds[QualityMetric.MSE]['excellent']:
                status = ValidationStatus.PASSED
            elif mse_value <= self.thresholds[QualityMetric.MSE]['acceptable']:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.MSE,
                value=mse_value,
                max_value=1000.0,
                threshold=self.thresholds[QualityMetric.MSE]['acceptable'],
                normalized_score=normalized_score,
                status=status,
                notes=f"MSE: {mse_value:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating MSE: {e}")
            return QualityScore(
                metric=QualityMetric.MSE,
                value=1000.0,
                max_value=1000.0,
                threshold=100.0,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_visual_quality(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate visual quality score"""
        try:
            # Edge preservation assessment
            original_edges = cv2.Canny(cv2.cvtColor(original, cv2.COLOR_RGB2GRAY), 50, 150)
            watermarked_edges = cv2.Canny(cv2.cvtColor(watermarked, cv2.COLOR_RGB2GRAY), 50, 150)
            
            edge_preservation = np.sum(original_edges & watermarked_edges) / (np.sum(original_edges) + 1e-10)
            
            # Texture preservation
            original_texture = cv2.Laplacian(cv2.cvtColor(original, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
            watermarked_texture = cv2.Laplacian(cv2.cvtColor(watermarked, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
            
            texture_preservation = 1.0 - abs(original_texture - watermarked_texture) / (original_texture + 1e-10)
            texture_preservation = max(0, min(1, texture_preservation))
            
            # Combined visual quality
            visual_quality = (edge_preservation + texture_preservation) / 2.0
            
            # Status determination
            if visual_quality >= 0.95:
                status = ValidationStatus.PASSED
            elif visual_quality >= 0.85:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.IMPERCEPTIBILITY,
                value=visual_quality,
                max_value=1.0,
                threshold=0.85,
                normalized_score=visual_quality,
                status=status,
                notes=f"Visual quality: {visual_quality:.3f} (edges: {edge_preservation:.3f}, texture: {texture_preservation:.3f})"
            )
            
        except Exception as e:
            logger.error(f"Error calculating visual quality: {e}")
            return QualityScore(
                metric=QualityMetric.IMPERCEPTIBILITY,
                value=0.0,
                max_value=1.0,
                threshold=0.85,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    async def _calculate_color_fidelity(self, original: np.ndarray, watermarked: np.ndarray) -> QualityScore:
        """Calculate color fidelity preservation"""
        try:
            # Color histogram comparison
            color_diff = 0.0
            for channel in range(min(original.shape[2], watermarked.shape[2])):
                orig_hist = cv2.calcHist([original], [channel], None, [256], [0, 256])
                water_hist = cv2.calcHist([watermarked], [channel], None, [256], [0, 256])
                
                # Normalize histograms
                orig_hist = orig_hist / (np.sum(orig_hist) + 1e-10)
                water_hist = water_hist / (np.sum(water_hist) + 1e-10)
                
                # Calculate correlation
                correlation = cv2.compareHist(orig_hist, water_hist, cv2.HISTCMP_CORREL)
                color_diff += (1.0 - correlation)
            
            color_diff /= original.shape[2]  # Average across channels
            color_fidelity = 1.0 - color_diff
            
            # Status determination
            if color_fidelity >= 0.98:
                status = ValidationStatus.PASSED
            elif color_fidelity >= 0.90:
                status = ValidationStatus.WARNING
            else:
                status = ValidationStatus.FAILED
            
            return QualityScore(
                metric=QualityMetric.ROBUSTNESS,  # Using as proxy for color fidelity
                value=color_fidelity,
                max_value=1.0,
                threshold=0.90,
                normalized_score=color_fidelity,
                status=status,
                notes=f"Color fidelity: {color_fidelity:.4f}"
            )
            
        except Exception as e:
            logger.error(f"Error calculating color fidelity: {e}")
            return QualityScore(
                metric=QualityMetric.ROBUSTNESS,
                value=0.0,
                max_value=1.0,
                threshold=0.90,
                normalized_score=0.0,
                status=ValidationStatus.ERROR,
                notes=f"Error: {str(e)}"
            )
    
    def _determine_overall_status(self, scores: List[QualityScore]) -> ValidationStatus:
        """Determine overall validation status"""
        failed_count = sum(1 for score in scores if score.status == ValidationStatus.FAILED)
        warning_count = sum(1 for score in scores if score.status == ValidationStatus.WARNING)
        error_count = sum(1 for score in scores if score.status == ValidationStatus.ERROR)
        
        if error_count > 0:
            return ValidationStatus.ERROR
        elif failed_count > 0:
            return ValidationStatus.FAILED
        elif warning_count > 0:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.PASSED
    
    def _generate_image_recommendations(self, scores: List[QualityScore]) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        for score in scores:
            if score.status == ValidationStatus.FAILED:
                if score.metric == QualityMetric.PSNR:
                    recommendations.append("Reduce watermark strength to improve PSNR")
                elif score.metric == QualityMetric.SSIM:
                    recommendations.append("Use DCT or DWT domain embedding to preserve structure")
                elif score.metric == QualityMetric.MSE:
                    recommendations.append("Apply adaptive embedding based on image complexity")
                elif score.metric == QualityMetric.IMPERCEPTIBILITY:
                    recommendations.append("Preserve edges and textures with selective embedding")
        
        if not recommendations:
            recommendations.append("Image quality is excellent - no improvements needed")
        
        return recommendations


class WatermarkValidationSystem:
    """
    Professional Watermark Quality Validation System
    
    Comprehensive quality assessment and validation for all content types
    with detailed reporting and recommendations.
    """
    
    def __init__(self):
        self.audio_assessor = AudioQualityAssessor()
        self.image_assessor = ImageQualityAssessor()
        self.validation_history: List[QualityAssessmentResult] = []
    
    async def validate_watermarked_content(self,
                                         original_content: Union[np.ndarray, str],
                                         watermarked_content: Union[np.ndarray, str],
                                         content_type: str,
                                         validation_config: Optional[Dict[str, Any]] = None) -> QualityAssessmentResult:
        """
        Validate watermarked content quality
        
        Args:
            original_content: Original content (array or file path)
            watermarked_content: Watermarked content (array or file path)
            content_type: Type of content ('audio', 'image', 'video', 'text')
            validation_config: Optional validation configuration
            
        Returns:
            QualityAssessmentResult with comprehensive metrics
        """
        try:
            # Load content if file paths provided
            if isinstance(original_content, str):
                original_data = await self._load_content(original_content, content_type)
            else:
                original_data = original_content
            
            if isinstance(watermarked_content, str):
                watermarked_data = await self._load_content(watermarked_content, content_type)
            else:
                watermarked_data = watermarked_content
            
            # Perform validation based on content type
            if content_type.lower() == 'audio':
                result = await self.audio_assessor.assess_audio_quality(original_data, watermarked_data)
            elif content_type.lower() == 'image':
                result = await self.image_assessor.assess_image_quality(original_data, watermarked_data)
            elif content_type.lower() == 'video':
                # TODO: Implement video validation
                result = await self._validate_video_quality(original_data, watermarked_data)
            elif content_type.lower() == 'text':
                # TODO: Implement text validation
                result = await self._validate_text_quality(original_data, watermarked_data)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Store validation history
            self.validation_history.append(result)
            
            # Log results
            logger.info(f"Quality validation completed for {content_type}: "
                       f"Score={result.overall_score:.3f}, Status={result.overall_status.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in content validation: {e}")
            raise
    
    async def _load_content(self, file_path: str, content_type: str) -> np.ndarray:
        """Load content from file"""
        try:
            file_path = Path(file_path)
            
            if content_type.lower() == 'audio':
                audio_data, _ = librosa.load(str(file_path), sr=None)
                return audio_data
            elif content_type.lower() == 'image':
                image = Image.open(file_path)
                return np.array(image)
            else:
                raise ValueError(f"Loading not implemented for content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error loading content from {file_path}: {e}")
            raise
    
    async def _validate_video_quality(self, original: np.ndarray, watermarked: np.ndarray) -> QualityAssessmentResult:
        """Validate video quality (placeholder)"""
        # TODO: Implement comprehensive video quality assessment
        return QualityAssessmentResult(
            content_type="video",
            assessment_timestamp=datetime.now(),
            overall_score=0.5,
            overall_status=ValidationStatus.PENDING,
            individual_scores=[],
            recommendations=["Video quality assessment not yet implemented"],
            processing_time_seconds=0.0
        )
    
    async def _validate_text_quality(self, original: str, watermarked: str) -> QualityAssessmentResult:
        """Validate text quality (placeholder)"""
        # TODO: Implement text quality assessment (readability, coherence, etc.)
        return QualityAssessmentResult(
            content_type="text",
            assessment_timestamp=datetime.now(),
            overall_score=0.5,
            overall_status=ValidationStatus.PENDING,
            individual_scores=[],
            recommendations=["Text quality assessment not yet implemented"],
            processing_time_seconds=0.0
        )
    
    async def batch_validate(self, 
                           validation_tasks: List[Tuple[str, str, str]]) -> List[QualityAssessmentResult]:
        """
        Batch validation of multiple content items
        
        Args:
            validation_tasks: List of (original_path, watermarked_path, content_type) tuples
            
        Returns:
            List of QualityAssessmentResult
        """
        try:
            results = []
            
            for original_path, watermarked_path, content_type in validation_tasks:
                try:
                    result = await self.validate_watermarked_content(
                        original_path, watermarked_path, content_type
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error validating {original_path}: {e}")
                    # Create error result
                    error_result = QualityAssessmentResult(
                        content_type=content_type,
                        assessment_timestamp=datetime.now(),
                        overall_score=0.0,
                        overall_status=ValidationStatus.ERROR,
                        individual_scores=[],
                        recommendations=[f"Validation failed: {str(e)}"],
                        processing_time_seconds=0.0
                    )
                    results.append(error_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch validation: {e}")
            return []
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics from history"""
        try:
            if not self.validation_history:
                return {"message": "No validation history available"}
            
            total_validations = len(self.validation_history)
            
            # Status distribution
            status_counts = {}
            for result in self.validation_history:
                status = result.overall_status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Content type distribution
            content_type_counts = {}
            for result in self.validation_history:
                content_type = result.content_type
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
            
            # Score statistics
            scores = [result.overall_score for result in self.validation_history]
            score_stats = {
                'mean': statistics.mean(scores),
                'median': statistics.median(scores),
                'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
                'min': min(scores),
                'max': max(scores)
            }
            
            return {
                'total_validations': total_validations,
                'status_distribution': status_counts,
                'content_type_distribution': content_type_counts,
                'score_statistics': score_stats,
                'last_validation': self.validation_history[-1].assessment_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating validation statistics: {e}")
            return {"error": str(e)}
    
    def export_validation_report(self, 
                               output_path: Optional[str] = None,
                               format: str = 'json') -> bool:
        """Export comprehensive validation report"""
        try:
            if not self.validation_history:
                logger.warning("No validation history to export")
                return False
            
            # Prepare report data
            report_data = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_validations': len(self.validation_history),
                    'report_format': format
                },
                'validation_statistics': self.get_validation_statistics(),
                'validation_results': [result.to_dict() for result in self.validation_history]
            }
            
            # Determine output path
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f'watermark_validation_report_{timestamp}.json'
            
            # Write report
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            logger.info(f"Validation report exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting validation report: {e}")
            return False


# Factory function
def create_validation_system() -> WatermarkValidationSystem:
    """Create validation system with standard configuration"""
    return WatermarkValidationSystem()


__all__ = [
    'WatermarkValidationSystem',
    'AudioQualityAssessor',
    'ImageQualityAssessor',
    'QualityAssessmentResult',
    'QualityScore',
    'QualityMetric',
    'QualityThreshold',
    'ValidationStatus',
    'create_validation_system'
]
