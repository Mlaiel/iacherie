"""
Voice Quality Assessment Module - IA Influencer Agent

Professional voice quality assessment and metrics calculation for content creators
and broadcasting standards compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import time

from .config import QualityConfig
from .models import VoiceQualityMetrics

logger = logging.getLogger(__name__)

class VoiceQualityAssessor:
    """Professional voice quality assessment system"""
    
    def __init__(self, config: QualityConfig):
        self.config = config
        self.is_initialized = False
        self.quality_models = {}
        
    async def initialize(self) -> bool:
        try:
            self.quality_models = {
                "perceptual": {"loaded": self.config.enable_perceptual_metrics},
                "objective": {"loaded": self.config.enable_objective_metrics},
                "professional": {"loaded": self.config.enable_professional_standards}
            }
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize quality assessor: {e}")
            return False
    
    async def assess_quality(self,
                           audio_data: np.ndarray,
                           sample_rate: int = 16000,
                           include_detailed_analysis: bool = False,
                           professional_standards: bool = False) -> VoiceQualityMetrics:
        """Assess comprehensive voice quality metrics"""
        try:
            # Calculate basic quality metrics
            snr = self._calculate_snr(audio_data)
            thd = self._calculate_thd(audio_data, sample_rate)
            dynamic_range = self._calculate_dynamic_range(audio_data)
            
            # Voice-specific metrics
            clarity = self._assess_clarity(audio_data, sample_rate)
            naturalness = self._assess_naturalness(audio_data, sample_rate)
            intelligibility = self._assess_intelligibility(audio_data, sample_rate)
            prosody = self._assess_prosody(audio_data, sample_rate)
            
            # Technical measurements
            peak_level = float(np.max(np.abs(audio_data)))
            rms_level = float(np.sqrt(np.mean(audio_data ** 2)))
            lufs = self._calculate_lufs(audio_data, sample_rate)
            
            # Professional standards compliance
            broadcast_compliant = self._check_broadcast_compliance(snr, dynamic_range, lufs)
            streaming_compliant = self._check_streaming_compliance(peak_level, rms_level)
            professional_grade = snr > 20 and clarity > 0.8 and naturalness > 0.8
            
            # Overall quality score
            overall_quality = (clarity + naturalness + intelligibility + prosody) / 4.0
            
            return VoiceQualityMetrics(
                overall_quality_score=overall_quality,
                signal_to_noise_ratio=snr,
                total_harmonic_distortion=thd,
                dynamic_range=dynamic_range,
                frequency_response_flatness=0.85,  # Mock value
                clarity_score=clarity,
                naturalness_score=naturalness,
                intelligibility_score=intelligibility,
                prosody_score=prosody,
                peak_level=peak_level,
                rms_level=rms_level,
                lufs_integrated=lufs,
                broadcast_standard_compliance=broadcast_compliant,
                streaming_platform_compliance=streaming_compliant,
                professional_grade=professional_grade
            )
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio"""
        # Simple SNR estimation
        signal_power = np.mean(audio ** 2)
        noise_estimate = np.percentile(np.abs(audio), 10) ** 2
        
        if noise_estimate > 0:
            snr_linear = signal_power / noise_estimate
            snr_db = 10 * np.log10(snr_linear)
            return float(snr_db)
        return 60.0  # High SNR if no noise detected
    
    def _calculate_thd(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate Total Harmonic Distortion"""
        # Simplified THD calculation
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        
        # Find fundamental frequency
        freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
        fundamental_idx = np.argmax(magnitude[:len(magnitude)//2])
        
        if fundamental_idx > 0:
            fundamental_power = magnitude[fundamental_idx] ** 2
            
            # Estimate harmonic distortion
            harmonic_power = 0
            for h in range(2, 6):  # 2nd to 5th harmonics
                harmonic_idx = fundamental_idx * h
                if harmonic_idx < len(magnitude):
                    harmonic_power += magnitude[harmonic_idx] ** 2
            
            if fundamental_power > 0:
                thd = np.sqrt(harmonic_power / fundamental_power) * 100
                return float(thd)
        
        return 1.0  # Low distortion default
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range in dB"""
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            dynamic_range = 20 * np.log10(peak / rms)
            return float(dynamic_range)
        return 0.0
    
    def _assess_clarity(self, audio: np.ndarray, sample_rate: int) -> float:
        """Assess voice clarity"""
        # Mock clarity assessment based on spectral characteristics
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        
        # High-frequency content indicates clarity
        high_freq_energy = np.sum(magnitude[len(magnitude)//4:len(magnitude)//2])
        total_energy = np.sum(magnitude[:len(magnitude)//2])
        
        if total_energy > 0:
            clarity_ratio = high_freq_energy / total_energy
            return min(1.0, clarity_ratio * 2.0)
        return 0.5
    
    def _assess_naturalness(self, audio: np.ndarray, sample_rate: int) -> float:
        """Assess voice naturalness"""
        # Mock naturalness assessment
        # In real implementation would use perceptual models
        return 0.85
    
    def _assess_intelligibility(self, audio: np.ndarray, sample_rate: int) -> float:
        """Assess speech intelligibility"""
        # Mock intelligibility assessment
        snr = self._calculate_snr(audio)
        intelligibility = min(1.0, (snr - 10) / 30)  # Maps 10-40 dB SNR to 0-1
        return max(0.0, intelligibility)
    
    def _assess_prosody(self, audio: np.ndarray, sample_rate: int) -> float:
        """Assess prosodic quality"""
        # Mock prosody assessment based on pitch variation
        # In real implementation would analyze intonation patterns
        return 0.80
    
    def _calculate_lufs(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate LUFS (Loudness Units relative to Full Scale)"""
        # Simplified LUFS calculation
        rms = np.sqrt(np.mean(audio ** 2))
        lufs = -23.0 + 20 * np.log10(rms + 1e-10)  # Approximate LUFS
        return float(lufs)
    
    def _check_broadcast_compliance(self, snr: float, dynamic_range: float, lufs: float) -> bool:
        """Check broadcast standard compliance"""
        return snr > 20 and dynamic_range > 12 and -30 < lufs < -16
    
    def _check_streaming_compliance(self, peak_level: float, rms_level: float) -> bool:
        """Check streaming platform compliance"""
        return peak_level < 0.95 and rms_level > 0.1
    
    async def shutdown(self) -> None:
        self.is_initialized = False

# Support classes
class QualityMetricsCalculator:
    def __init__(self, assessor: VoiceQualityAssessor):
        self.assessor = assessor
    
    async def calculate_metrics(self, audio: np.ndarray) -> Dict[str, float]:
        result = await self.assessor.assess_quality(audio)
        return result.to_dict()

class PerceptualAnalyzer:
    def __init__(self, assessor: VoiceQualityAssessor):
        self.assessor = assessor
    
    async def analyze_perceptual_quality(self, audio: np.ndarray) -> Dict[str, float]:
        result = await self.assessor.assess_quality(audio)
        return {
            "clarity": result.clarity_score,
            "naturalness": result.naturalness_score,
            "intelligibility": result.intelligibility_score,
            "prosody": result.prosody_score
        }

class ProfessionalStandardsValidator:
    def __init__(self, assessor: VoiceQualityAssessor):
        self.assessor = assessor
    
    async def validate_standards(self, audio: np.ndarray) -> Dict[str, bool]:
        result = await self.assessor.assess_quality(audio, professional_standards=True)
        return {
            "broadcast_compliant": result.broadcast_standard_compliance,
            "streaming_compliant": result.streaming_platform_compliance,
            "professional_grade": result.professional_grade
        }

class QualityReporter:
    def __init__(self, assessor: VoiceQualityAssessor):
        self.assessor = assessor
    
    async def generate_quality_report(self, audio: np.ndarray) -> Dict[str, Any]:
        result = await self.assessor.assess_quality(audio, include_detailed_analysis=True)
        
        return {
            "overall_score": result.overall_quality_score,
            "grade": "Professional" if result.professional_grade else "Standard",
            "recommendations": self._generate_recommendations(result),
            "technical_metrics": {
                "snr": result.signal_to_noise_ratio,
                "thd": result.total_harmonic_distortion,
                "dynamic_range": result.dynamic_range,
                "lufs": result.lufs_integrated
            },
            "perceptual_scores": {
                "clarity": result.clarity_score,
                "naturalness": result.naturalness_score,
                "intelligibility": result.intelligibility_score,
                "prosody": result.prosody_score
            }
        }
    
    def _generate_recommendations(self, metrics: VoiceQualityMetrics) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if metrics.signal_to_noise_ratio < 20:
            recommendations.append("Improve recording environment to reduce background noise")
        
        if metrics.clarity_score < 0.7:
            recommendations.append("Use better microphone positioning for improved clarity")
        
        if metrics.naturalness_score < 0.7:
            recommendations.append("Practice more natural speech patterns")
        
        if metrics.peak_level > 0.9:
            recommendations.append("Reduce input gain to prevent clipping")
        
        if not recommendations:
            recommendations.append("Voice quality is excellent - no improvements needed")
        
        return recommendations
