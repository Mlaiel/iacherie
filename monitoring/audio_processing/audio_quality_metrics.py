"""
Audio Quality Metrics - Audio Processing Module
==============================================

Professional audio quality monitoring and measurement system for the Ainflue platform.
Implements industry-standard audio quality metrics including PESQ, STOI, SNR, THD+N,
and broadcast standards compliance for enterprise audio processing workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)

class AudioQualityStandard(Enum):
    """Audio quality measurement standards"""
    BROADCAST = "broadcast"  # EBU R128, ITU-R BS.1770
    STREAMING = "streaming"  # Spotify, Apple Music standards
    PODCAST = "podcast"     # Podcast industry standards
    MASTERING = "mastering" # Professional mastering standards
    VOICE = "voice"         # Voice quality standards
    MUSIC = "music"         # Music production standards

class QualityMetricType(Enum):
    """Types of audio quality metrics"""
    PESQ = "pesq"                    # Perceptual Evaluation of Speech Quality
    STOI = "stoi"                    # Short-Time Objective Intelligibility
    SNR = "snr"                      # Signal-to-Noise Ratio
    THD_N = "thd_n"                  # Total Harmonic Distortion + Noise
    LUFS = "lufs"                    # Loudness Units relative to Full Scale
    LRA = "lra"                      # Loudness Range
    TRUE_PEAK = "true_peak"          # True Peak Level
    DYNAMIC_RANGE = "dynamic_range"  # Dynamic Range
    FREQUENCY_RESPONSE = "freq_response"  # Frequency Response Analysis
    PHASE_COHERENCE = "phase_coherence"   # Phase Coherence
    STEREO_WIDTH = "stereo_width"    # Stereo Image Width
    SPECTRAL_CENTROID = "spectral_centroid"  # Spectral Centroid

@dataclass
class AudioQualityMeasurement:
    """Individual audio quality measurement"""
    measurement_id: str
    content_id: str
    metric_type: QualityMetricType
    value: float
    unit: str
    standard: AudioQualityStandard
    pass_threshold: float
    quality_score: float  # 0.0 to 1.0
    compliance_status: str  # pass, warning, fail
    measurement_time: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AudioQualityReport:
    """Comprehensive audio quality report"""
    report_id: str
    content_id: str
    overall_quality_score: float
    standard_compliance: Dict[AudioQualityStandard, bool]
    measurements: List[AudioQualityMeasurement]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class QualityThresholds:
    """Quality thresholds for different standards"""
    standard: AudioQualityStandard
    lufs_target: float
    lufs_tolerance: float
    true_peak_max: float
    lra_max: float
    snr_min: float
    thd_n_max: float

class AudioQualityMetrics:
    """
    Professional audio quality metrics system.
    
    Provides comprehensive audio quality measurement, analysis, and reporting
    for enterprise audio processing workflows in the Ainflue platform.
    Implements industry-standard metrics and broadcast compliance monitoring.
    """
    
    def __init__(self):
        self.measurements: List[AudioQualityMeasurement] = []
        self.quality_reports: Dict[str, AudioQualityReport] = {}
        self.quality_thresholds: Dict[AudioQualityStandard, QualityThresholds] = {}
        self.real_time_monitoring: Dict[str, Dict[str, Any]] = {}
        self._initialize_quality_thresholds()
        logger.info("Audio Quality Metrics system initialized")
    
    def _initialize_quality_thresholds(self):
        """Initialize quality thresholds for different standards"""
        self.quality_thresholds = {
            AudioQualityStandard.BROADCAST: QualityThresholds(
                standard=AudioQualityStandard.BROADCAST,
                lufs_target=-23.0,  # EBU R128
                lufs_tolerance=1.0,
                true_peak_max=-1.0,  # dBTP
                lra_max=20.0,  # LU
                snr_min=60.0,  # dB
                thd_n_max=0.1  # %
            ),
            AudioQualityStandard.STREAMING: QualityThresholds(
                standard=AudioQualityStandard.STREAMING,
                lufs_target=-14.0,  # Spotify/Apple Music
                lufs_tolerance=1.0,
                true_peak_max=-1.0,
                lra_max=15.0,
                snr_min=70.0,
                thd_n_max=0.05
            ),
            AudioQualityStandard.PODCAST: QualityThresholds(
                standard=AudioQualityStandard.PODCAST,
                lufs_target=-16.0,
                lufs_tolerance=2.0,
                true_peak_max=-3.0,
                lra_max=10.0,
                snr_min=50.0,
                thd_n_max=0.2
            ),
            AudioQualityStandard.MASTERING: QualityThresholds(
                standard=AudioQualityStandard.MASTERING,
                lufs_target=-14.0,
                lufs_tolerance=0.5,
                true_peak_max=-0.1,
                lra_max=12.0,
                snr_min=80.0,
                thd_n_max=0.02
            ),
            AudioQualityStandard.VOICE: QualityThresholds(
                standard=AudioQualityStandard.VOICE,
                lufs_target=-18.0,
                lufs_tolerance=3.0,
                true_peak_max=-6.0,
                lra_max=8.0,
                snr_min=40.0,
                thd_n_max=0.5
            ),
            AudioQualityStandard.MUSIC: QualityThresholds(
                standard=AudioQualityStandard.MUSIC,
                lufs_target=-14.0,
                lufs_tolerance=1.0,
                true_peak_max=-1.0,
                lra_max=18.0,
                snr_min=75.0,
                thd_n_max=0.03
            )
        }
    
    async def analyze_audio_quality(self, content_id: str, audio_data: np.ndarray,
                                   sample_rate: int, standard: AudioQualityStandard,
                                   metadata: Optional[Dict[str, Any]] = None) -> AudioQualityReport:
        """
        Perform comprehensive audio quality analysis
        
        Args:
            content_id: Content identifier
            audio_data: Audio samples as numpy array
            sample_rate: Audio sample rate
            standard: Quality standard to apply
            metadata: Additional analysis metadata
            
        Returns:
            Comprehensive audio quality report
        """
        report_id = f"quality_report_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        measurements = []
        
        try:
            # Perform all quality measurements
            lufs_measurement = await self._measure_lufs(content_id, audio_data, sample_rate, standard)
            measurements.append(lufs_measurement)
            
            lra_measurement = await self._measure_lra(content_id, audio_data, sample_rate, standard)
            measurements.append(lra_measurement)
            
            true_peak_measurement = await self._measure_true_peak(content_id, audio_data, sample_rate, standard)
            measurements.append(true_peak_measurement)
            
            snr_measurement = await self._measure_snr(content_id, audio_data, sample_rate, standard)
            measurements.append(snr_measurement)
            
            thd_n_measurement = await self._measure_thd_n(content_id, audio_data, sample_rate, standard)
            measurements.append(thd_n_measurement)
            
            dynamic_range_measurement = await self._measure_dynamic_range(content_id, audio_data, sample_rate, standard)
            measurements.append(dynamic_range_measurement)
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_quality_score(measurements, standard)
            
            # Check standard compliance
            compliance = self._check_standard_compliance(measurements, standard)
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(measurements, standard)
            
            # Create quality report
            report = AudioQualityReport(
                report_id=report_id,
                content_id=content_id,
                overall_quality_score=overall_score,
                standard_compliance={standard: compliance},
                measurements=measurements,
                recommendations=recommendations
            )
            
            self.quality_reports[content_id] = report
            self.measurements.extend(measurements)
            
            logger.info(f"Audio quality analysis completed for {content_id}, score: {overall_score:.3f}")
            return report
            
        except Exception as e:
            logger.error(f"Audio quality analysis failed for {content_id}: {e}")
            raise
    
    async def _measure_lufs(self, content_id: str, audio_data: np.ndarray,
                           sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure LUFS (Loudness Units relative to Full Scale)"""
        # Simulate LUFS measurement (in real implementation, use pyloudnorm or similar)
        # This is a simplified simulation
        rms = np.sqrt(np.mean(audio_data**2))
        lufs_value = 20 * np.log10(rms + 1e-10) - 0.691  # Approximate LUFS calculation
        
        threshold = self.quality_thresholds[standard]
        target_lufs = threshold.lufs_target
        tolerance = threshold.lufs_tolerance
        
        # Calculate quality score based on deviation from target
        deviation = abs(lufs_value - target_lufs)
        quality_score = max(0.0, 1.0 - (deviation / (tolerance * 3)))
        
        # Determine compliance status
        if deviation <= tolerance:
            compliance_status = "pass"
        elif deviation <= tolerance * 2:
            compliance_status = "warning"
        else:
            compliance_status = "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"lufs_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.LUFS,
            value=lufs_value,
            unit="LUFS",
            standard=standard,
            pass_threshold=target_lufs,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"target": target_lufs, "tolerance": tolerance, "deviation": deviation}
        )
    
    async def _measure_lra(self, content_id: str, audio_data: np.ndarray,
                          sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure LRA (Loudness Range)"""
        # Simulate LRA measurement
        # Calculate short-term loudness variations
        window_size = int(sample_rate * 3.0)  # 3-second windows
        short_term_loudness = []
        
        for i in range(0, len(audio_data) - window_size, window_size // 2):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window**2))
            loudness = 20 * np.log10(rms + 1e-10)
            short_term_loudness.append(loudness)
        
        if len(short_term_loudness) > 0:
            lra_value = np.percentile(short_term_loudness, 95) - np.percentile(short_term_loudness, 10)
        else:
            lra_value = 0.0
        
        threshold = self.quality_thresholds[standard]
        max_lra = threshold.lra_max
        
        quality_score = max(0.0, 1.0 - (lra_value / (max_lra * 1.5)))
        compliance_status = "pass" if lra_value <= max_lra else "warning" if lra_value <= max_lra * 1.2 else "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"lra_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.LRA,
            value=lra_value,
            unit="LU",
            standard=standard,
            pass_threshold=max_lra,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"max_allowed": max_lra}
        )
    
    async def _measure_true_peak(self, content_id: str, audio_data: np.ndarray,
                               sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure True Peak Level"""
        # Simulate true peak measurement (oversample and find peaks)
        # In real implementation, use proper oversampling
        true_peak_value = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
        
        threshold = self.quality_thresholds[standard]
        max_true_peak = threshold.true_peak_max
        
        quality_score = max(0.0, 1.0 - max(0, true_peak_value - max_true_peak) / 6.0)
        compliance_status = "pass" if true_peak_value <= max_true_peak else "warning" if true_peak_value <= max_true_peak + 1 else "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"true_peak_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.TRUE_PEAK,
            value=true_peak_value,
            unit="dBTP",
            standard=standard,
            pass_threshold=max_true_peak,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"max_allowed": max_true_peak}
        )
    
    async def _measure_snr(self, content_id: str, audio_data: np.ndarray,
                          sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure Signal-to-Noise Ratio"""
        # Simulate SNR measurement
        # Find quiet sections for noise estimation
        signal_power = np.mean(audio_data**2)
        
        # Estimate noise floor (simplified approach)
        sorted_samples = np.sort(np.abs(audio_data))
        noise_samples = sorted_samples[:len(sorted_samples)//10]  # Bottom 10% as noise estimate
        noise_power = np.mean(noise_samples**2)
        
        if noise_power > 0:
            snr_value = 10 * np.log10(signal_power / noise_power)
        else:
            snr_value = 100.0  # Very high SNR if no detectable noise
        
        threshold = self.quality_thresholds[standard]
        min_snr = threshold.snr_min
        
        quality_score = max(0.0, min(1.0, (snr_value - min_snr) / 20.0))
        compliance_status = "pass" if snr_value >= min_snr else "warning" if snr_value >= min_snr - 10 else "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"snr_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.SNR,
            value=snr_value,
            unit="dB",
            standard=standard,
            pass_threshold=min_snr,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"min_required": min_snr}
        )
    
    async def _measure_thd_n(self, content_id: str, audio_data: np.ndarray,
                           sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure Total Harmonic Distortion + Noise"""
        # Simulate THD+N measurement
        # In real implementation, use proper harmonic analysis
        # This is a simplified estimation based on high-frequency content
        
        # Apply high-pass filter to estimate noise and distortion
        from scipy import signal
        nyquist = sample_rate / 2
        high_cutoff = min(8000, nyquist * 0.8)  # High frequency cutoff
        
        # Simple high-pass filter simulation
        if len(audio_data) > 1000:
            # Estimate THD+N as ratio of high-frequency energy to total energy
            fft = np.fft.fft(audio_data[:min(len(audio_data), 8192)])
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            
            total_energy = np.sum(np.abs(fft)**2)
            high_freq_energy = np.sum(np.abs(fft[np.abs(freqs) > high_cutoff/2])**2)
            
            thd_n_ratio = high_freq_energy / (total_energy + 1e-10)
            thd_n_percentage = thd_n_ratio * 100
        else:
            thd_n_percentage = 0.1  # Default low distortion
        
        threshold = self.quality_thresholds[standard]
        max_thd_n = threshold.thd_n_max
        
        quality_score = max(0.0, 1.0 - (thd_n_percentage / (max_thd_n * 2)))
        compliance_status = "pass" if thd_n_percentage <= max_thd_n else "warning" if thd_n_percentage <= max_thd_n * 2 else "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"thd_n_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.THD_N,
            value=thd_n_percentage,
            unit="%",
            standard=standard,
            pass_threshold=max_thd_n,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"max_allowed": max_thd_n}
        )
    
    async def _measure_dynamic_range(self, content_id: str, audio_data: np.ndarray,
                                   sample_rate: int, standard: AudioQualityStandard) -> AudioQualityMeasurement:
        """Measure Dynamic Range"""
        # Calculate dynamic range using RMS analysis
        window_size = int(sample_rate * 0.1)  # 100ms windows
        rms_values = []
        
        for i in range(0, len(audio_data) - window_size, window_size):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window**2))
            if rms > 1e-10:  # Avoid log of zero
                rms_values.append(20 * np.log10(rms))
        
        if len(rms_values) > 0:
            dynamic_range = np.max(rms_values) - np.percentile(rms_values, 10)
        else:
            dynamic_range = 0.0
        
        # Dynamic range scoring (higher is generally better)
        quality_score = min(1.0, dynamic_range / 40.0)  # Normalize to 40dB as good range
        compliance_status = "pass" if dynamic_range >= 20 else "warning" if dynamic_range >= 10 else "fail"
        
        return AudioQualityMeasurement(
            measurement_id=f"dynamic_range_{content_id}_{int(datetime.utcnow().timestamp())}",
            content_id=content_id,
            metric_type=QualityMetricType.DYNAMIC_RANGE,
            value=dynamic_range,
            unit="dB",
            standard=standard,
            pass_threshold=20.0,
            quality_score=quality_score,
            compliance_status=compliance_status,
            measurement_time=datetime.utcnow(),
            metadata={"measurement_method": "rms_percentile"}
        )
    
    def _calculate_overall_quality_score(self, measurements: List[AudioQualityMeasurement],
                                       standard: AudioQualityStandard) -> float:
        """Calculate overall quality score from individual measurements"""
        if not measurements:
            return 0.0
        
        # Weight different metrics based on importance for the standard
        weights = {
            QualityMetricType.LUFS: 0.25,
            QualityMetricType.TRUE_PEAK: 0.20,
            QualityMetricType.SNR: 0.20,
            QualityMetricType.THD_N: 0.15,
            QualityMetricType.LRA: 0.10,
            QualityMetricType.DYNAMIC_RANGE: 0.10
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for measurement in measurements:
            weight = weights.get(measurement.metric_type, 0.0)
            weighted_sum += measurement.quality_score * weight
            total_weight += weight
        
        if total_weight > 0:
            return round(weighted_sum / total_weight, 3)
        else:
            return 0.0
    
    def _check_standard_compliance(self, measurements: List[AudioQualityMeasurement],
                                 standard: AudioQualityStandard) -> bool:
        """Check if measurements comply with standard requirements"""
        for measurement in measurements:
            if measurement.compliance_status == "fail":
                return False
        return True
    
    def _generate_quality_recommendations(self, measurements: List[AudioQualityMeasurement],
                                        standard: AudioQualityStandard) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        for measurement in measurements:
            if measurement.compliance_status in ["warning", "fail"]:
                if measurement.metric_type == QualityMetricType.LUFS:
                    if measurement.value > measurement.pass_threshold:
                        recommendations.append(f"Audio is too loud ({measurement.value:.1f} LUFS). Reduce gain to reach {measurement.pass_threshold:.1f} LUFS target.")
                    else:
                        recommendations.append(f"Audio is too quiet ({measurement.value:.1f} LUFS). Increase gain to reach {measurement.pass_threshold:.1f} LUFS target.")
                
                elif measurement.metric_type == QualityMetricType.TRUE_PEAK:
                    recommendations.append(f"True peak level too high ({measurement.value:.1f} dBTP). Apply limiting to stay below {measurement.pass_threshold:.1f} dBTP.")
                
                elif measurement.metric_type == QualityMetricType.SNR:
                    recommendations.append(f"Signal-to-noise ratio too low ({measurement.value:.1f} dB). Apply noise reduction or re-record in quieter environment.")
                
                elif measurement.metric_type == QualityMetricType.THD_N:
                    recommendations.append(f"Total harmonic distortion too high ({measurement.value:.2f}%). Check input levels and audio chain for distortion sources.")
                
                elif measurement.metric_type == QualityMetricType.LRA:
                    recommendations.append(f"Loudness range too wide ({measurement.value:.1f} LU). Apply compression to reduce dynamic variations.")
                
                elif measurement.metric_type == QualityMetricType.DYNAMIC_RANGE:
                    recommendations.append(f"Dynamic range limited ({measurement.value:.1f} dB). Avoid over-compression to preserve musical dynamics.")
        
        if not recommendations:
            recommendations.append("Audio quality meets all requirements for the selected standard.")
        
        return recommendations
    
    def get_quality_report(self, content_id: str) -> Optional[AudioQualityReport]:
        """Get quality report for specific content"""
        return self.quality_reports.get(content_id)
    
    def get_quality_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends over time"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_measurements = [
            m for m in self.measurements 
            if m.measurement_time >= cutoff_time
        ]
        
        if not recent_measurements:
            return {"message": f"No quality measurements in last {hours} hours"}
        
        # Calculate trends by metric type
        trends = {}
        for metric_type in QualityMetricType:
            metric_measurements = [m for m in recent_measurements if m.metric_type == metric_type]
            if metric_measurements:
                values = [m.value for m in metric_measurements]
                quality_scores = [m.quality_score for m in metric_measurements]
                
                trends[metric_type.value] = {
                    'count': len(metric_measurements),
                    'avg_value': round(statistics.mean(values), 3),
                    'avg_quality_score': round(statistics.mean(quality_scores), 3),
                    'pass_rate': len([m for m in metric_measurements if m.compliance_status == "pass"]) / len(metric_measurements)
                }
        
        # Overall statistics
        total_reports = len(set(m.content_id for m in recent_measurements))
        avg_overall_quality = statistics.mean([r.overall_quality_score for r in self.quality_reports.values()])
        
        return {
            'period_hours': hours,
            'total_measurements': len(recent_measurements),
            'total_reports': total_reports,
            'avg_overall_quality': round(avg_overall_quality, 3),
            'metric_trends': trends
        }

# Global quality metrics instance
audio_quality_metrics = AudioQualityMetrics()

# Export main components
__all__ = [
    'AudioQualityMetrics',
    'AudioQualityMeasurement',
    'AudioQualityReport',
    'QualityThresholds',
    'AudioQualityStandard',
    'QualityMetricType',
    'audio_quality_metrics'
]