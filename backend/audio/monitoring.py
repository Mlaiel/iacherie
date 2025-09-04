"""📊 Audio Processing Monitoring Module - Professional Quality Control & Monitoring

Advanced audio processing monitoring, quality control, compliance checking, and performance analytics
for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque


class QualityStandard(Enum):
    """Audio quality standards"""
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    CD_QUALITY = "cd_quality"
    PODCAST = "podcast"
    VOICE = "voice"
    CUSTOM = "custom"


@dataclass
class QualityThresholds:
    """Quality control thresholds"""
    min_snr_db: float = 40.0
    max_thd_percent: float = 1.0
    min_dynamic_range_db: float = 20.0
    max_peak_db: float = -3.0
    target_lufs: float = -23.0
    max_clipping_percent: float = 0.1


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    processing_time: float
    cpu_usage: float
    memory_usage: float
    throughput_mbps: float
    latency_ms: float
    queue_depth: int


class AudioValidator:
    """✅ Professional Audio Quality Validator"""
    
    def __init__(self, standard: QualityStandard = QualityStandard.BROADCAST):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.standard = standard
        self.thresholds = self._get_quality_thresholds(standard)
    
    def validate_audio(self, audio_data: np.ndarray, sample_rate: int = 44100) -> Dict[str, Any]:
        """Validate audio against quality standards"""
        results = {
            "passed": True,
            "violations": [],
            "metrics": {},
            "score": 0.0
        }
        
        # Check SNR
        snr = self._calculate_snr(audio_data)
        results["metrics"]["snr_db"] = snr
        if snr < self.thresholds.min_snr_db:
            results["passed"] = False
            results["violations"].append(f"SNR too low: {snr:.1f}dB < {self.thresholds.min_snr_db}dB")
        
        # Check THD
        thd = self._calculate_thd(audio_data)
        results["metrics"]["thd_percent"] = thd
        if thd > self.thresholds.max_thd_percent:
            results["passed"] = False
            results["violations"].append(f"THD too high: {thd:.2f}% > {self.thresholds.max_thd_percent}%")
        
        # Check dynamic range
        dynamic_range = self._calculate_dynamic_range(audio_data)
        results["metrics"]["dynamic_range_db"] = dynamic_range
        if dynamic_range < self.thresholds.min_dynamic_range_db:
            results["passed"] = False
            results["violations"].append(f"Dynamic range too low: {dynamic_range:.1f}dB")
        
        # Check peak levels
        peak_db = self._calculate_peak_db(audio_data)
        results["metrics"]["peak_db"] = peak_db
        if peak_db > self.thresholds.max_peak_db:
            results["passed"] = False
            results["violations"].append(f"Peak too high: {peak_db:.1f}dB")
        
        # Check clipping
        clipping_percent = self._detect_clipping(audio_data)
        results["metrics"]["clipping_percent"] = clipping_percent
        if clipping_percent > self.thresholds.max_clipping_percent:
            results["passed"] = False
            results["violations"].append(f"Too much clipping: {clipping_percent:.2f}%")
        
        # Calculate overall score
        results["score"] = self._calculate_quality_score(results["metrics"])
        
        return results
    
    def _get_quality_thresholds(self, standard: QualityStandard) -> QualityThresholds:
        """Get quality thresholds for standard"""
        standards = {
            QualityStandard.BROADCAST: QualityThresholds(
                min_snr_db=50.0, max_thd_percent=0.5, min_dynamic_range_db=25.0,
                max_peak_db=-1.0, target_lufs=-23.0, max_clipping_percent=0.01
            ),
            QualityStandard.STREAMING: QualityThresholds(
                min_snr_db=40.0, max_thd_percent=1.0, min_dynamic_range_db=20.0,
                max_peak_db=-3.0, target_lufs=-14.0, max_clipping_percent=0.1
            ),
            QualityStandard.CD_QUALITY: QualityThresholds(
                min_snr_db=60.0, max_thd_percent=0.1, min_dynamic_range_db=30.0,
                max_peak_db=-0.1, target_lufs=-16.0, max_clipping_percent=0.0
            ),
            QualityStandard.PODCAST: QualityThresholds(
                min_snr_db=35.0, max_thd_percent=2.0, min_dynamic_range_db=15.0,
                max_peak_db=-6.0, target_lufs=-16.0, max_clipping_percent=0.5
            )
        }
        return standards.get(standard, QualityThresholds())
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        signal_power = np.mean(audio_data ** 2)
        # Estimate noise from quietest 10% of samples
        noise_samples = np.sort(np.abs(audio_data))[:len(audio_data)//10]
        noise_power = np.mean(noise_samples ** 2)
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        return float(snr)
    
    def _calculate_thd(self, audio_data: np.ndarray) -> float:
        """Calculate total harmonic distortion"""
        # Simplified THD calculation
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Find fundamental frequency
        fundamental_idx = np.argmax(magnitude[1:]) + 1
        fundamental_power = magnitude[fundamental_idx] ** 2
        
        # Calculate harmonics (simplified)
        harmonics_power = 0
        for harmonic in range(2, 6):  # 2nd to 5th harmonic
            harmonic_idx = fundamental_idx * harmonic
            if harmonic_idx < len(magnitude):
                harmonics_power += magnitude[harmonic_idx] ** 2
        
        thd = np.sqrt(harmonics_power / (fundamental_power + 1e-10)) * 100
        return float(thd)
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range"""
        peak = np.max(np.abs(audio_data))
        noise_floor = np.percentile(np.abs(audio_data), 10)
        dr = 20 * np.log10(peak / (noise_floor + 1e-10))
        return float(dr)
    
    def _calculate_peak_db(self, audio_data: np.ndarray) -> float:
        """Calculate peak level in dB"""
        peak = np.max(np.abs(audio_data))
        peak_db = 20 * np.log10(peak + 1e-10)
        return float(peak_db)
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect clipping percentage"""
        threshold = 0.99
        clipped_samples = np.sum(np.abs(audio_data) >= threshold)
        clipping_percent = (clipped_samples / len(audio_data)) * 100
        return float(clipping_percent)
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0
        
        # Deduct points for violations
        snr = metrics.get("snr_db", 0)
        if snr < self.thresholds.min_snr_db:
            score -= (self.thresholds.min_snr_db - snr) * 2
        
        thd = metrics.get("thd_percent", 0)
        if thd > self.thresholds.max_thd_percent:
            score -= (thd - self.thresholds.max_thd_percent) * 10
        
        clipping = metrics.get("clipping_percent", 0)
        score -= clipping * 5
        
        return max(0.0, min(100.0, float(score)))


class QualityMetrics:
    """📊 Comprehensive Audio Quality Metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_comprehensive_metrics(self, audio_data: np.ndarray, 
                                      sample_rate: int = 44100) -> Dict[str, float]:
        """Calculate comprehensive quality metrics"""
        metrics = {}
        
        # Basic metrics
        metrics["duration"] = len(audio_data) / sample_rate
        metrics["sample_rate"] = sample_rate
        metrics["channels"] = 1 if audio_data.ndim == 1 else audio_data.shape[0]
        
        # Level metrics
        metrics["peak_level_db"] = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
        metrics["rms_level_db"] = 20 * np.log10(np.sqrt(np.mean(audio_data ** 2)) + 1e-10)
        
        # Dynamic metrics
        metrics["dynamic_range_db"] = self._calculate_dynamic_range(audio_data)
        metrics["crest_factor_db"] = metrics["peak_level_db"] - metrics["rms_level_db"]
        
        # Spectral metrics
        spectral_metrics = self._calculate_spectral_metrics(audio_data, sample_rate)
        metrics.update(spectral_metrics)
        
        # Quality indicators
        metrics["snr_db"] = self._calculate_snr(audio_data)
        metrics["thd_percent"] = self._calculate_thd(audio_data)
        metrics["clipping_percent"] = self._detect_clipping(audio_data)
        
        return {k: float(v) for k, v in metrics.items()}
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range"""
        peak = np.max(np.abs(audio_data))
        noise_floor = np.percentile(np.abs(audio_data), 10)
        return 20 * np.log10(peak / (noise_floor + 1e-10))
    
    def _calculate_spectral_metrics(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Calculate spectral quality metrics"""
        # FFT analysis
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)[:len(magnitude)]
        
        # Spectral centroid
        spectral_centroid = np.sum(freqs * magnitude) / (np.sum(magnitude) + 1e-10)
        
        # Spectral bandwidth
        centroid_deviation = (freqs - spectral_centroid) ** 2
        spectral_bandwidth = np.sqrt(np.sum(centroid_deviation * magnitude) / (np.sum(magnitude) + 1e-10))
        
        # Spectral rolloff (95% of energy)
        cumulative_energy = np.cumsum(magnitude ** 2)
        total_energy = cumulative_energy[-1]
        rolloff_threshold = 0.95 * total_energy
        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
        spectral_rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else freqs[-1]
        
        return {
            "spectral_centroid_hz": spectral_centroid,
            "spectral_bandwidth_hz": spectral_bandwidth,
            "spectral_rolloff_hz": spectral_rolloff
        }
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate SNR"""
        signal_power = np.mean(audio_data ** 2)
        noise_samples = np.sort(np.abs(audio_data))[:len(audio_data)//10]
        noise_power = np.mean(noise_samples ** 2)
        return 10 * np.log10(signal_power / (noise_power + 1e-10))
    
    def _calculate_thd(self, audio_data: np.ndarray) -> float:
        """Calculate THD"""
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        fundamental_idx = np.argmax(magnitude[1:]) + 1
        fundamental_power = magnitude[fundamental_idx] ** 2
        
        harmonics_power = 0
        for harmonic in range(2, 6):
            harmonic_idx = fundamental_idx * harmonic
            if harmonic_idx < len(magnitude):
                harmonics_power += magnitude[harmonic_idx] ** 2
        
        return np.sqrt(harmonics_power / (fundamental_power + 1e-10)) * 100
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect clipping"""
        clipped_samples = np.sum(np.abs(audio_data) >= 0.99)
        return (clipped_samples / len(audio_data)) * 100


class ComplianceChecker:
    """⚖️ Broadcast & Streaming Compliance Checker"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.compliance_standards = {
            "EBU_R128": {"target_lufs": -23.0, "max_peak": -1.0},
            "ATSC_A85": {"target_lufs": -24.0, "max_peak": -2.0},
            "Spotify": {"target_lufs": -14.0, "max_peak": -1.0},
            "YouTube": {"target_lufs": -14.0, "max_peak": -1.0},
            "Apple_Music": {"target_lufs": -16.0, "max_peak": -1.0}
        }
    
    def check_compliance(self, audio_data: np.ndarray, 
                        standard: str = "EBU_R128") -> Dict[str, Any]:
        """Check compliance with broadcast/streaming standards"""
        if standard not in self.compliance_standards:
            return {"error": f"Unknown standard: {standard}"}
        
        std = self.compliance_standards[standard]
        
        # Measure loudness (simplified LUFS estimation)
        lufs = self._estimate_lufs(audio_data)
        
        # Measure peak
        peak_db = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
        
        # Check compliance
        lufs_compliant = abs(lufs - std["target_lufs"]) <= 1.0
        peak_compliant = peak_db <= std["max_peak"]
        
        return {
            "standard": standard,
            "compliant": lufs_compliant and peak_compliant,
            "measured_lufs": lufs,
            "target_lufs": std["target_lufs"],
            "lufs_compliant": lufs_compliant,
            "measured_peak_db": peak_db,
            "max_peak_db": std["max_peak"],
            "peak_compliant": peak_compliant
        }
    
    def _estimate_lufs(self, audio_data: np.ndarray) -> float:
        """Simplified LUFS estimation"""
        # Simplified implementation - real LUFS requires proper filtering
        rms = np.sqrt(np.mean(audio_data ** 2))
        lufs_estimate = 20 * np.log10(rms + 1e-10) - 0.691
        return float(lufs_estimate)


class MasteringStandards:
    """🎯 Professional Mastering Standards"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def evaluate_mastering_quality(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Evaluate mastering quality"""
        results = {
            "overall_grade": "C",
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Check loudness consistency
        loudness_consistency = self._check_loudness_consistency(audio_data)
        results["metrics"]["loudness_consistency"] = loudness_consistency
        
        # Check frequency balance
        frequency_balance = self._check_frequency_balance(audio_data)
        results["metrics"]["frequency_balance"] = frequency_balance
        
        # Check stereo imaging
        stereo_score = self._check_stereo_imaging(audio_data)
        results["metrics"]["stereo_imaging"] = stereo_score
        
        # Generate overall grade
        overall_score = (loudness_consistency + frequency_balance + stereo_score) / 3
        
        if overall_score >= 0.9:
            results["overall_grade"] = "A"
        elif overall_score >= 0.8:
            results["overall_grade"] = "B"
        elif overall_score >= 0.6:
            results["overall_grade"] = "C"
        else:
            results["overall_grade"] = "D"
        
        return results
    
    def _check_loudness_consistency(self, audio_data: np.ndarray) -> float:
        """Check loudness consistency across time"""
        # Split into segments and check RMS variation
        segment_size = len(audio_data) // 10
        if segment_size < 1024:
            return 1.0
        
        segment_rms = []
        for i in range(0, len(audio_data) - segment_size, segment_size):
            segment = audio_data[i:i + segment_size]
            rms = np.sqrt(np.mean(segment ** 2))
            segment_rms.append(rms)
        
        if not segment_rms:
            return 1.0
        
        # Calculate consistency (lower variation = higher score)
        variation = np.std(segment_rms) / (np.mean(segment_rms) + 1e-10)
        consistency = 1.0 / (1.0 + variation * 10)
        
        return float(consistency)
    
    def _check_frequency_balance(self, audio_data: np.ndarray) -> float:
        """Check frequency balance"""
        # Analyze frequency distribution
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Divide into frequency bands
        band_size = len(magnitude) // 5
        band_energies = []
        
        for i in range(5):
            start_idx = i * band_size
            end_idx = (i + 1) * band_size
            band_energy = np.sum(magnitude[start_idx:end_idx] ** 2)
            band_energies.append(band_energy)
        
        # Check balance (penalize extreme imbalances)
        total_energy = sum(band_energies)
        if total_energy == 0:
            return 1.0
        
        band_ratios = [energy / total_energy for energy in band_energies]
        
        # Ideal would be relatively balanced
        balance_score = 1.0 - np.std(band_ratios) * 5
        
        return max(0.0, min(1.0, float(balance_score)))
    
    def _check_stereo_imaging(self, audio_data: np.ndarray) -> float:
        """Check stereo imaging quality"""
        if audio_data.ndim == 1:
            return 0.5  # Mono content
        
        left = audio_data[0] if audio_data.ndim == 2 else audio_data
        right = audio_data[1] if audio_data.ndim == 2 and audio_data.shape[0] >= 2 else left
        
        # Calculate correlation between channels
        correlation = np.corrcoef(left, right)[0, 1] if len(left) > 1 else 1.0
        
        # Good stereo imaging has some correlation but not perfect
        if 0.3 <= correlation <= 0.8:
            return 1.0
        elif correlation > 0.8:
            return 0.7  # Too similar
        else:
            return 0.5  # Too different or uncorrelated
        
        return float(correlation)


class DistortionAnalyzer:
    """🔍 Advanced Distortion Analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_distortion(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Analyze various types of distortion"""
        results = {}
        
        # THD analysis
        results["thd_percent"] = self._calculate_thd(audio_data)
        
        # IMD analysis (simplified)
        results["imd_percent"] = self._calculate_imd(audio_data)
        
        # Clipping detection
        results["clipping_percent"] = self._detect_clipping(audio_data)
        
        # Aliasing detection
        results["aliasing_score"] = self._detect_aliasing(audio_data)
        
        return results
    
    def _calculate_thd(self, audio_data: np.ndarray) -> float:
        """Calculate THD"""
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        fundamental_idx = np.argmax(magnitude[1:]) + 1
        fundamental_power = magnitude[fundamental_idx] ** 2
        
        harmonics_power = 0
        for harmonic in range(2, 10):
            harmonic_idx = fundamental_idx * harmonic
            if harmonic_idx < len(magnitude):
                harmonics_power += magnitude[harmonic_idx] ** 2
        
        return np.sqrt(harmonics_power / (fundamental_power + 1e-10)) * 100
    
    def _calculate_imd(self, audio_data: np.ndarray) -> float:
        """Calculate intermodulation distortion (simplified)"""
        # Simplified IMD calculation
        return self._calculate_thd(audio_data) * 0.7  # Rough estimation
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect clipping"""
        clipped_samples = np.sum(np.abs(audio_data) >= 0.99)
        return (clipped_samples / len(audio_data)) * 100
    
    def _detect_aliasing(self, audio_data: np.ndarray) -> float:
        """Detect aliasing artifacts"""
        # Look for high-frequency content that might indicate aliasing
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Check energy in upper frequencies
        upper_quarter = magnitude[3*len(magnitude)//4:]
        total_energy = np.sum(magnitude ** 2)
        upper_energy = np.sum(upper_quarter ** 2)
        
        aliasing_ratio = upper_energy / (total_energy + 1e-10)
        aliasing_score = min(aliasing_ratio * 10, 1.0)
        
        return float(aliasing_score)


class DynamicRangeAnalyzer:
    """📊 Dynamic Range Analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_dynamic_range(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Comprehensive dynamic range analysis"""
        results = {}
        
        # Peak-to-RMS ratio
        peak = np.max(np.abs(audio_data))
        rms = np.sqrt(np.mean(audio_data ** 2))
        results["peak_to_rms_db"] = 20 * np.log10(peak / (rms + 1e-10))
        
        # Dynamic range (peak to noise floor)
        noise_floor = np.percentile(np.abs(audio_data), 10)
        results["dynamic_range_db"] = 20 * np.log10(peak / (noise_floor + 1e-10))
        
        # Loudness range (simplified)
        results["loudness_range_lu"] = self._calculate_loudness_range(audio_data)
        
        # Compression detection
        results["compression_ratio"] = self._detect_compression(audio_data)
        
        return results
    
    def _calculate_loudness_range(self, audio_data: np.ndarray) -> float:
        """Calculate loudness range"""
        # Simplified LRA calculation
        # Split into short segments and measure loudness variation
        segment_size = len(audio_data) // 20
        if segment_size < 512:
            return 0.0
        
        segment_loudness = []
        for i in range(0, len(audio_data) - segment_size, segment_size):
            segment = audio_data[i:i + segment_size]
            loudness = 20 * np.log10(np.sqrt(np.mean(segment ** 2)) + 1e-10)
            segment_loudness.append(loudness)
        
        if len(segment_loudness) < 2:
            return 0.0
        
        # LRA is roughly the difference between 95th and 10th percentile
        lra = np.percentile(segment_loudness, 95) - np.percentile(segment_loudness, 10)
        return float(lra)
    
    def _detect_compression(self, audio_data: np.ndarray) -> float:
        """Detect compression ratio"""
        # Analyze envelope dynamics
        envelope = np.abs(audio_data)
        
        # Smooth envelope
        from scipy.ndimage import uniform_filter1d
        smoothed_envelope = uniform_filter1d(envelope, size=1024)
        
        # Calculate compression by looking at envelope variation
        env_std = np.std(smoothed_envelope)
        env_mean = np.mean(smoothed_envelope)
        
        # High compression = low variation relative to mean
        if env_mean > 0:
            compression_indicator = 1.0 - (env_std / env_mean)
            compression_ratio = max(1.0, compression_indicator * 10)
        else:
            compression_ratio = 1.0
        
        return float(compression_ratio)


class PerformanceMonitor:
    """⚡ Processing Performance Monitor"""
    
    def __init__(self, history_size: int = 100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.history_size = history_size
        self.processing_times = deque(maxlen=history_size)
        self.throughput_history = deque(maxlen=history_size)
        self.memory_usage_history = deque(maxlen=history_size)
    
    def record_processing_metrics(self, metrics: ProcessingMetrics):
        """Record processing performance metrics"""
        self.processing_times.append(metrics.processing_time)
        self.throughput_history.append(metrics.throughput_mbps)
        self.memory_usage_history.append(metrics.memory_usage)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if not self.processing_times:
            return {}
        
        return {
            "avg_processing_time": float(np.mean(self.processing_times)),
            "max_processing_time": float(np.max(self.processing_times)),
            "min_processing_time": float(np.min(self.processing_times)),
            "avg_throughput_mbps": float(np.mean(self.throughput_history)) if self.throughput_history else 0.0,
            "avg_memory_usage": float(np.mean(self.memory_usage_history)) if self.memory_usage_history else 0.0,
            "samples_recorded": len(self.processing_times)
        }


class ProcessingStats:
    """📈 Processing Statistics Collector"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stats = {
            "total_processed": 0,
            "total_processing_time": 0.0,
            "error_count": 0,
            "format_counts": {},
            "quality_scores": []
        }
    
    def record_processing(self, format_type: str, processing_time: float, 
                         quality_score: float, success: bool = True):
        """Record processing statistics"""
        self.stats["total_processed"] += 1
        self.stats["total_processing_time"] += processing_time
        
        if not success:
            self.stats["error_count"] += 1
        
        # Track format usage
        if format_type not in self.stats["format_counts"]:
            self.stats["format_counts"][format_type] = 0
        self.stats["format_counts"][format_type] += 1
        
        # Track quality scores
        self.stats["quality_scores"].append(quality_score)
        
        # Keep only last 1000 quality scores
        if len(self.stats["quality_scores"]) > 1000:
            self.stats["quality_scores"] = self.stats["quality_scores"][-1000:]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        summary = self.stats.copy()
        
        if self.stats["quality_scores"]:
            summary["avg_quality_score"] = float(np.mean(self.stats["quality_scores"]))
            summary["min_quality_score"] = float(np.min(self.stats["quality_scores"]))
            summary["max_quality_score"] = float(np.max(self.stats["quality_scores"]))
        
        if self.stats["total_processed"] > 0:
            summary["avg_processing_time"] = self.stats["total_processing_time"] / self.stats["total_processed"]
            summary["error_rate"] = self.stats["error_count"] / self.stats["total_processed"]
        
        return summary


__all__ = [
    'AudioValidator', 'QualityMetrics', 'ComplianceChecker', 'MasteringStandards',
    'DistortionAnalyzer', 'DynamicRangeAnalyzer', 'PerformanceMonitor', 'ProcessingStats'
]