"""Audio Quality Configuration Module for IA-Influencer Agent Platform
==================================================================

Professional audio quality assessment and optimization configuration.
Supports comprehensive quality metrics and enhancement strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Audio quality metrics"""    SNR = "signal_noise_ratio"
    THD = "total_harmonic_distortion"
    DYNAMIC_RANGE = "dynamic_range"
    PEAK_RMS_RATIO = "peak_rms_ratio"
    SPECTRAL_FLATNESS = "spectral_flatness"
    FREQUENCY_RESPONSE = "frequency_response"
    PHASE_COHERENCE = "phase_coherence"
    STEREO_IMAGING = "stereo_imaging"
    LOUDNESS_LUFS = "loudness_lufs"
    PEAK_LEVEL = "peak_level"
    CLIPPING_DETECTION = "clipping_detection"
    NOISE_FLOOR = "noise_floor"


class QualityGrade(Enum):
    """Audio quality grades"""    EXCELLENT = "excellent"      # 90-100%
    GOOD = "good"               # 75-89%
    ACCEPTABLE = "acceptable"    # 60-74%
    POOR = "poor"               # 40-59%
    UNACCEPTABLE = "unacceptable"  # 0-39%


class QualityStandard(Enum):
    """Audio quality standards"""    BROADCAST = "broadcast"      # EBU R128, ITU-R BS.1770
    STREAMING = "streaming"      # Platform-specific standards
    MASTERING = "mastering"      # Professional mastering standards
    PODCAST = "podcast"          # Podcast-specific standards
    MOBILE = "mobile"           # Mobile-optimized standards
    VOIP = "voip"              # Voice over IP standards


class AnalysisDepth(Enum):
    """Quality analysis depth levels"""    QUICK = "quick"             # Basic metrics only
    STANDARD = "standard"       # Standard quality assessment
    COMPREHENSIVE = "comprehensive"  # Full quality analysis
    FORENSIC = "forensic"       # Detailed forensic analysis


@dataclass
class QualityThresholds:
    """Quality assessment thresholds"""    excellent_threshold: float = 90.0
    good_threshold: float = 75.0
    acceptable_threshold: float = 60.0
    poor_threshold: float = 40.0
    
    # Specific metric thresholds
    min_snr_db: float = 20.0
    max_thd_percent: float = 1.0
    min_dynamic_range_db: float = 12.0
    max_peak_lufs: float = -1.0
    min_loudness_lufs: float = -30.0
    max_loudness_lufs: float = -6.0


@dataclass
class PerceptualQualityConfig:
    """Perceptual quality assessment configuration"""    enable_psychoacoustic_model: bool = True
    use_bark_scale: bool = True
    use_critical_bands: bool = True
    masking_threshold_analysis: bool = True
    temporal_masking: bool = True
    frequency_masking: bool = True
    loudness_weighting: bool = True


@dataclass
class TechnicalQualityConfig:
    """Technical quality assessment configuration"""    analyze_frequency_response: bool = True
    analyze_phase_response: bool = True
    analyze_harmonic_distortion: bool = True
    analyze_intermodulation: bool = False
    analyze_noise_spectrum: bool = True
    analyze_dynamic_range: bool = True
    analyze_stereo_characteristics: bool = True


@dataclass
class EnhancementConfig:
    """Quality enhancement configuration"""    enable_noise_reduction: bool = True
    enable_dynamic_range_enhancement: bool = True
    enable_spectral_enhancement: bool = True
    enable_stereo_enhancement: bool = False
    enable_harmonic_enhancement: bool = False
    enhancement_strength: float = 0.5  # 0.0-1.0
    preserve_original_character: bool = True


class AudioQualityConfig:
    """    Comprehensive audio quality configuration manager
    
    Manages quality assessment metrics, thresholds, standards compliance,
    and enhancement strategies for professional audio processing.
    """    
    def __init__(self):
        """Initialize audio quality configuration"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core configuration
        self._quality_standard = QualityStandard.STREAMING
        self._analysis_depth = AnalysisDepth.STANDARD
        self._target_grade = QualityGrade.GOOD
        
        # Configuration objects
        self.quality_thresholds = QualityThresholds()
        self.perceptual_config = PerceptualQualityConfig()
        self.technical_config = TechnicalQualityConfig()
        self.enhancement_config = EnhancementConfig()
        
        # Enabled metrics
        self._enabled_metrics = [
            QualityMetric.SNR,
            QualityMetric.DYNAMIC_RANGE,
            QualityMetric.LOUDNESS_LUFS,
            QualityMetric.PEAK_LEVEL,
            QualityMetric.THD
        ]
        
        # Standard-specific configurations
        self._standard_configs = self._initialize_standard_configs()
        
        # Quality profiles for different use cases
        self._quality_profiles = self._initialize_quality_profiles()
        
        # Metric weights for overall quality scoring
        self._metric_weights = self._initialize_metric_weights()
        
        self.logger.info("AudioQualityConfig initialized successfully")
    
    def _initialize_standard_configs(self) -> Dict[QualityStandard, Dict[str, Any]]:
        """Initialize quality standard configurations"""        return {
            QualityStandard.BROADCAST: {
                "name": "Broadcast Standard (EBU R128)",
                "description": "Professional broadcast audio quality standards",
                "target_lufs": -23.0,
                "max_peak_dbfs": -1.0,
                "max_short_term_lufs": -18.0,
                "max_momentary_lufs": -18.0,
                "loudness_range_target": "7-20 LU",
                "frequency_response": {
                    "tolerance_db": 0.5,
                    "range_hz": (20, 20000)
                },
                "thresholds": QualityThresholds(
                    min_snr_db=40.0,
                    max_thd_percent=0.1,
                    min_dynamic_range_db=20.0,
                    max_peak_lufs=-1.0,
                    min_loudness_lufs=-30.0,
                    max_loudness_lufs=-18.0
                ),
                "requirements": {
                    "sample_rate_min": 48000,
                    "bit_depth_min": 24,
                    "channels_max": 8,
                    "format_requirements": ["wav", "bwf"]
                }
            },
            QualityStandard.STREAMING: {
                "name": "Streaming Quality Standard",
                "description": "High-quality streaming audio standards",
                "target_lufs": -14.0,
                "max_peak_dbfs": -1.0,
                "loudness_range_target": "4-12 LU",
                "frequency_response": {
                    "tolerance_db": 1.0,
                    "range_hz": (20, 20000)
                },
                "thresholds": QualityThresholds(
                    min_snr_db=30.0,
                    max_thd_percent=0.5,
                    min_dynamic_range_db=15.0,
                    max_peak_lufs=-1.0,
                    min_loudness_lufs=-25.0,
                    max_loudness_lufs=-10.0
                ),
                "platform_variants": {
                    "spotify": {"target_lufs": -14.0, "peak_limit": -2.0},
                    "apple_music": {"target_lufs": -16.0, "peak_limit": -1.0},
                    "youtube": {"target_lufs": -13.0, "peak_limit": -1.0}
                }
            },
            QualityStandard.MASTERING: {
                "name": "Professional Mastering Standard",
                "description": "High-end mastering quality standards",
                "target_lufs_range": (-16.0, -8.0),
                "max_peak_dbfs": -0.1,
                "frequency_response": {
                    "tolerance_db": 0.1,
                    "range_hz": (10, 22000)
                },
                "thresholds": QualityThresholds(
                    min_snr_db=60.0,
                    max_thd_percent=0.01,
                    min_dynamic_range_db=25.0,
                    max_peak_lufs=-0.1,
                    min_loudness_lufs=-35.0,
                    max_loudness_lufs=-6.0
                ),
                "requirements": {
                    "sample_rate_min": 96000,
                    "bit_depth_min": 24,
                    "format_requirements": ["wav", "flac", "dxd"]
                }
            },
            QualityStandard.PODCAST: {
                "name": "Podcast Quality Standard",
                "description": "Speech-optimized audio quality",
                "target_lufs": -19.0,
                "max_peak_dbfs": -3.0,
                "speech_intelligibility_weight": 0.4,
                "frequency_response": {
                    "tolerance_db": 2.0,
                    "range_hz": (100, 8000),
                    "speech_emphasis": True
                },
                "thresholds": QualityThresholds(
                    min_snr_db=25.0,
                    max_thd_percent=1.0,
                    min_dynamic_range_db=10.0,
                    max_peak_lufs=-3.0,
                    min_loudness_lufs=-30.0,
                    max_loudness_lufs=-12.0
                ),
                "speech_specific": {
                    "gate_threshold": -50.0,
                    "noise_reduction_strength": 0.7,
                    "compression_ratio": 3.0
                }
            },
            QualityStandard.MOBILE: {
                "name": "Mobile Optimized Standard",
                "description": "Mobile device optimized quality",
                "target_lufs": -16.0,
                "max_peak_dbfs": -2.0,
                "frequency_response": {
                    "tolerance_db": 3.0,
                    "range_hz": (50, 15000)
                },
                "thresholds": QualityThresholds(
                    min_snr_db=20.0,
                    max_thd_percent=2.0,
                    min_dynamic_range_db=8.0,
                    max_peak_lufs=-2.0,
                    min_loudness_lufs=-25.0,
                    max_loudness_lufs=-12.0
                ),
                "mobile_specific": {
                    "battery_efficiency": True,
                    "processing_limit": "moderate",
                    "bandwidth_optimization": True
                }
            },
            QualityStandard.VOIP: {
                "name": "Voice over IP Standard",
                "description": "VoIP communication quality",
                "target_lufs": -20.0,
                "frequency_response": {
                    "range_hz": (300, 3400),
                    "telephony_weighting": True
                },
                "thresholds": QualityThresholds(
                    min_snr_db=15.0,
                    max_thd_percent=5.0,
                    min_dynamic_range_db=6.0
                ),
                "voip_specific": {
                    "echo_cancellation": True,
                    "noise_suppression": True,
                    "automatic_gain_control": True,
                    "packet_loss_tolerance": 3.0
                }
            }
        }
    
    def _initialize_quality_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality assessment profiles"""        return {
            "music_production": {
                "description": "Music production quality assessment",
                "primary_metrics": [
                    QualityMetric.DYNAMIC_RANGE,
                    QualityMetric.FREQUENCY_RESPONSE,
                    QualityMetric.THD,
                    QualityMetric.STEREO_IMAGING,
                    QualityMetric.LOUDNESS_LUFS
                ],
                "analysis_depth": AnalysisDepth.COMPREHENSIVE,
                "enhancement_focus": ["dynamic_range", "spectral_balance"],
                "quality_standard": QualityStandard.MASTERING,
                "perceptual_weighting": 0.6,
                "technical_weighting": 0.4
            },
            "streaming_optimization": {
                "description": "Streaming platform optimization",
                "primary_metrics": [
                    QualityMetric.LOUDNESS_LUFS,
                    QualityMetric.PEAK_LEVEL,
                    QualityMetric.DYNAMIC_RANGE,
                    QualityMetric.FREQUENCY_RESPONSE
                ],
                "analysis_depth": AnalysisDepth.STANDARD,
                "enhancement_focus": ["loudness_normalization", "peak_limiting"],
                "quality_standard": QualityStandard.STREAMING,
                "platform_variants": True
            },
            "voice_content": {
                "description": "Voice and speech content assessment",
                "primary_metrics": [
                    QualityMetric.SNR,
                    QualityMetric.NOISE_FLOOR,
                    QualityMetric.FREQUENCY_RESPONSE,
                    QualityMetric.LOUDNESS_LUFS
                ],
                "analysis_depth": AnalysisDepth.STANDARD,
                "enhancement_focus": ["noise_reduction", "speech_clarity"],
                "quality_standard": QualityStandard.PODCAST,
                "speech_intelligibility_priority": True
            },
            "broadcast_ready": {
                "description": "Broadcast-ready content assessment",
                "primary_metrics": [
                    QualityMetric.LOUDNESS_LUFS,
                    QualityMetric.PEAK_LEVEL,
                    QualityMetric.DYNAMIC_RANGE,
                    QualityMetric.FREQUENCY_RESPONSE,
                    QualityMetric.PHASE_COHERENCE
                ],
                "analysis_depth": AnalysisDepth.COMPREHENSIVE,
                "enhancement_focus": ["ebu_r128_compliance"],
                "quality_standard": QualityStandard.BROADCAST,
                "compliance_checking": True
            },
            "mobile_content": {
                "description": "Mobile device optimized content",
                "primary_metrics": [
                    QualityMetric.LOUDNESS_LUFS,
                    QualityMetric.DYNAMIC_RANGE,
                    QualityMetric.FREQUENCY_RESPONSE
                ],
                "analysis_depth": AnalysisDepth.QUICK,
                "enhancement_focus": ["mobile_optimization"],
                "quality_standard": QualityStandard.MOBILE,
                "processing_efficiency": True
            },
            "archival_quality": {
                "description": "Archival quality assessment",
                "primary_metrics": [
                    QualityMetric.SNR,
                    QualityMetric.THD,
                    QualityMetric.FREQUENCY_RESPONSE,
                    QualityMetric.PHASE_COHERENCE,
                    QualityMetric.DYNAMIC_RANGE
                ],
                "analysis_depth": AnalysisDepth.FORENSIC,
                "enhancement_focus": ["preservation", "restoration"],
                "quality_standard": QualityStandard.MASTERING,
                "historical_comparison": True
            }
        }
    
    def _initialize_metric_weights(self) -> Dict[QualityMetric, float]:
        """Initialize metric weights for overall quality scoring"""        return {
            QualityMetric.SNR: 0.15,
            QualityMetric.THD: 0.10,
            QualityMetric.DYNAMIC_RANGE: 0.20,
            QualityMetric.PEAK_RMS_RATIO: 0.05,
            QualityMetric.SPECTRAL_FLATNESS: 0.10,
            QualityMetric.FREQUENCY_RESPONSE: 0.15,
            QualityMetric.PHASE_COHERENCE: 0.05,
            QualityMetric.STEREO_IMAGING: 0.05,
            QualityMetric.LOUDNESS_LUFS: 0.10,
            QualityMetric.PEAK_LEVEL: 0.05,
            QualityMetric.CLIPPING_DETECTION: 0.15,
            QualityMetric.NOISE_FLOOR: 0.10
        }
    
    def get_quality_standard_config(self, standard: QualityStandard) -> Dict[str, Any]:
        """        Get configuration for specific quality standard
        
        Args:
            standard: Quality standard
            
        Returns:
            Standard configuration
        """        return self._standard_configs.get(standard, {})
    
    def get_quality_profile(self, profile_name: str) -> Dict[str, Any]:
        """        Get quality assessment profile
        
        Args:
            profile_name: Name of the quality profile
            
        Returns:
            Quality profile configuration
        """        return self._quality_profiles.get(profile_name, {})
    
    def apply_quality_profile(self, profile_name: str) -> bool:
        """        Apply quality assessment profile
        
        Args:
            profile_name: Name of the quality profile
            
        Returns:
            Success status
        """        try:
            profile = self.get_quality_profile(profile_name)
            if not profile:
                self.logger.error(f"Unknown quality profile: {profile_name}")
                return False
            
            # Apply primary metrics
            if "primary_metrics" in profile:
                self._enabled_metrics = profile["primary_metrics"]
            
            # Apply analysis depth
            if "analysis_depth" in profile:
                self._analysis_depth = profile["analysis_depth"]
            
            # Apply quality standard
            if "quality_standard" in profile:
                self._quality_standard = profile["quality_standard"]
                standard_config = self._standard_configs[profile["quality_standard"]]
                if "thresholds" in standard_config:
                    self.quality_thresholds = standard_config["thresholds"]
            
            # Apply enhancement configuration
            if "enhancement_focus" in profile:
                focus_areas = profile["enhancement_focus"]
                if "noise_reduction" in focus_areas:
                    self.enhancement_config.enable_noise_reduction = True
                if "dynamic_range" in focus_areas:
                    self.enhancement_config.enable_dynamic_range_enhancement = True
                if "spectral_balance" in focus_areas:
                    self.enhancement_config.enable_spectral_enhancement = True
            
            # Configure analysis types based on profile
            if profile_name == "voice_content":
                self.technical_config.analyze_stereo_characteristics = False
                self.perceptual_config.loudness_weighting = True
            elif profile_name == "music_production":
                self.technical_config.analyze_stereo_characteristics = True
                self.technical_config.analyze_harmonic_distortion = True
            
            self.logger.info(f"Applied quality profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply quality profile: {e}")
            return False
    
    def calculate_quality_score(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """        Calculate overall quality score from individual metrics
        
        Args:
            metrics: Dictionary of metric values
            
        Returns:
            Quality score and analysis
        """        try:
            weighted_scores = []
            metric_scores = {}
            
            for metric_name, value in metrics.items():
                try:
                    metric = QualityMetric(metric_name)
                    if metric in self._enabled_metrics:
                        # Normalize metric to 0-100 scale
                        normalized_score = self._normalize_metric_value(metric, value)
                        weight = self._metric_weights.get(metric, 0.1)
                        weighted_score = normalized_score * weight
                        
                        weighted_scores.append(weighted_score)
                        metric_scores[metric.value] = {
                            "raw_value": value,
                            "normalized_score": normalized_score,
                            "weight": weight,
                            "weighted_score": weighted_score
                        }
                except ValueError:
                    self.logger.warning(f"Unknown metric: {metric_name}")
                    continue
            
            # Calculate overall score
            if weighted_scores:
                overall_score = sum(weighted_scores) / sum(
                    self._metric_weights[metric] 
                    for metric in self._enabled_metrics 
                    if metric.value in metrics
                )
            else:
                overall_score = 0.0
            
            # Determine quality grade
            quality_grade = self._determine_quality_grade(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metric_scores, overall_score)
            
            return {
                "overall_score": round(overall_score, 2),
                "quality_grade": quality_grade.value,
                "metric_scores": metric_scores,
                "recommendations": recommendations,
                "standard_compliance": self._check_standard_compliance(metrics),
                "improvement_potential": max(0, 100 - overall_score)
            }
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return {
                "overall_score": 0.0,
                "quality_grade": QualityGrade.UNACCEPTABLE.value,
                "error": str(e)
            }
    
    def _normalize_metric_value(self, metric: QualityMetric, value: float) -> float:
        """Normalize metric value to 0-100 scale"""        try:
            if metric == QualityMetric.SNR:
                # SNR: higher is better, normalize around 20-60dB range
                return min(100, max(0, (value - 10) * 2))
            
            elif metric == QualityMetric.THD:
                # THD: lower is better, invert scale
                thd_percent = value * 100 if value <= 1.0 else value
                return max(0, 100 - thd_percent * 20)
            
            elif metric == QualityMetric.DYNAMIC_RANGE:
                # Dynamic range: higher is better, normalize around 6-30dB
                return min(100, max(0, (value - 6) * 4))
            
            elif metric == QualityMetric.LOUDNESS_LUFS:
                # LUFS: depends on standard, normalize around target
                target = self._get_target_lufs()
                deviation = abs(value - target)
                return max(0, 100 - deviation * 5)
            
            elif metric == QualityMetric.PEAK_LEVEL:
                # Peak level: should be below 0dBFS
                if value <= -6.0:
                    return 100
                elif value >= 0.0:
                    return 0
                else:
                    return (100 + value * 16.67)  # Linear scale -6 to 0
            
            elif metric == QualityMetric.SPECTRAL_FLATNESS:
                # Spectral flatness: 0.5-0.9 is typically good
                if 0.5 <= value <= 0.9:
                    return 100
                else:
                    deviation = min(abs(value - 0.5), abs(value - 0.9))
                    return max(0, 100 - deviation * 200)
            
            else:
                # Default normalization for unknown metrics
                return min(100, max(0, value))
                
        except Exception:
            return 50.0  # Default middle value
    
    def _get_target_lufs(self) -> float:
        """Get target LUFS for current quality standard"""        standard_config = self._standard_configs.get(self._quality_standard, {})
        return standard_config.get("target_lufs", -16.0)
    
    def _determine_quality_grade(self, score: float) -> QualityGrade:
        """Determine quality grade from overall score"""        if score >= self.quality_thresholds.excellent_threshold:
            return QualityGrade.EXCELLENT
        elif score >= self.quality_thresholds.good_threshold:
            return QualityGrade.GOOD
        elif score >= self.quality_thresholds.acceptable_threshold:
            return QualityGrade.ACCEPTABLE
        elif score >= self.quality_thresholds.poor_threshold:
            return QualityGrade.POOR
        else:
            return QualityGrade.UNACCEPTABLE
    
    def _generate_recommendations(self, 
                                metric_scores: Dict[str, Dict[str, float]], 
                                overall_score: float) -> List[str]:
        """Generate quality improvement recommendations"""        recommendations = []
        
        try:
            # Analyze individual metrics for issues
            for metric_name, score_info in metric_scores.items():
                normalized_score = score_info["normalized_score"]
                raw_value = score_info["raw_value"]
                
                if normalized_score < 50:  # Poor metric score
                    if metric_name == QualityMetric.SNR.value:
                        recommendations.append(f"Improve signal-to-noise ratio (current: {raw_value:.1f}dB). Consider noise reduction.")
                    elif metric_name == QualityMetric.THD.value:
                        recommendations.append(f"Reduce harmonic distortion (current: {raw_value*100:.2f}%). Check gain staging.")
                    elif metric_name == QualityMetric.DYNAMIC_RANGE.value:
                        recommendations.append(f"Increase dynamic range (current: {raw_value:.1f}dB). Reduce compression.")
                    elif metric_name == QualityMetric.LOUDNESS_LUFS.value:
                        target = self._get_target_lufs()
                        if raw_value < target - 3:
                            recommendations.append(f"Audio too quiet ({raw_value:.1f} LUFS). Target: {target:.1f} LUFS.")
                        elif raw_value > target + 3:
                            recommendations.append(f"Audio too loud ({raw_value:.1f} LUFS). Target: {target:.1f} LUFS.")
                    elif metric_name == QualityMetric.PEAK_LEVEL.value:
                        recommendations.append(f"Peak level too high ({raw_value:.1f}dBFS). Apply limiting or reduce gain.")
            
            # Overall recommendations based on quality grade
            quality_grade = self._determine_quality_grade(overall_score)
            
            if quality_grade == QualityGrade.UNACCEPTABLE:
                recommendations.append("Audio quality is unacceptable. Major improvements needed.")
                recommendations.append("Consider re-recording or extensive post-processing.")
            elif quality_grade == QualityGrade.POOR:
                recommendations.append("Audio quality needs significant improvement.")
                recommendations.append("Focus on the lowest-scoring metrics first.")
            elif quality_grade == QualityGrade.ACCEPTABLE:
                recommendations.append("Audio quality is acceptable but could be enhanced.")
            
            # Enhancement-specific recommendations
            if self.enhancement_config.enable_noise_reduction:
                recommendations.append("Consider applying noise reduction if background noise is present.")
            
            if self.enhancement_config.enable_dynamic_range_enhancement:
                recommendations.append("Dynamic range enhancement may improve perceived quality.")
            
            # Standard-specific recommendations
            standard_config = self._standard_configs.get(self._quality_standard, {})
            if "requirements" in standard_config:
                requirements = standard_config["requirements"]
                if "sample_rate_min" in requirements:
                    recommendations.append(f"Ensure sample rate meets minimum requirement: {requirements['sample_rate_min']}Hz")
            
            # Remove duplicates and limit to top 5 recommendations
            unique_recommendations = list(dict.fromkeys(recommendations))[:5]
            
            return unique_recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate specific recommendations due to analysis error."]
    
    def _check_standard_compliance(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """Check compliance with current quality standard"""        compliance = {}
        
        try:
            standard_config = self._standard_configs.get(self._quality_standard, {})
            
            # Check LUFS compliance
            if "target_lufs" in standard_config and QualityMetric.LOUDNESS_LUFS.value in metrics:
                target = standard_config["target_lufs"]
                actual = metrics[QualityMetric.LOUDNESS_LUFS.value]
                compliance["loudness_compliance"] = abs(actual - target) <= 2.0
            
            # Check peak level compliance
            if "max_peak_dbfs" in standard_config and QualityMetric.PEAK_LEVEL.value in metrics:
                max_peak = standard_config["max_peak_dbfs"]
                actual_peak = metrics[QualityMetric.PEAK_LEVEL.value]
                compliance["peak_compliance"] = actual_peak <= max_peak
            
            # Check THD compliance
            if "thresholds" in standard_config:
                thresholds = standard_config["thresholds"]
                if QualityMetric.THD.value in metrics:
                    thd_value = metrics[QualityMetric.THD.value] * 100  # Convert to percentage
                    compliance["thd_compliance"] = thd_value <= thresholds.max_thd_percent
                
                # Check SNR compliance
                if QualityMetric.SNR.value in metrics:
                    snr_value = metrics[QualityMetric.SNR.value]
                    compliance["snr_compliance"] = snr_value >= thresholds.min_snr_db
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
        
        return compliance
    
    def create_quality_config(self, 
                            use_case: str,
                            quality_standard: Optional[QualityStandard] = None,
                            target_grade: Optional[QualityGrade] = None) -> Dict[str, Any]:
        """        Create complete quality assessment configuration
        
        Args:
            use_case: Quality assessment use case
            quality_standard: Target quality standard
            target_grade: Target quality grade
            
        Returns:
            Complete quality configuration
        """        try:
            # Apply appropriate profile based on use case
            if use_case in self._quality_profiles:
                self.apply_quality_profile(use_case)
            elif "music" in use_case.lower():
                self.apply_quality_profile("music_production")
            elif "speech" in use_case.lower() or "voice" in use_case.lower():
                self.apply_quality_profile("voice_content")
            elif "stream" in use_case.lower():
                self.apply_quality_profile("streaming_optimization")
            elif "broadcast" in use_case.lower():
                self.apply_quality_profile("broadcast_ready")
            elif "mobile" in use_case.lower():
                self.apply_quality_profile("mobile_content")
            
            # Override standard if specified
            if quality_standard:
                self._quality_standard = quality_standard
            
            # Override target grade if specified
            if target_grade:
                self._target_grade = target_grade
            
            return {
                "use_case": use_case,
                "quality_standard": self._quality_standard.value,
                "analysis_depth": self._analysis_depth.value,
                "target_grade": self._target_grade.value,
                "enabled_metrics": [metric.value for metric in self._enabled_metrics],
                "metric_weights": {metric.value: weight for metric, weight in self._metric_weights.items()},
                "quality_thresholds": {
                    "excellent_threshold": self.quality_thresholds.excellent_threshold,
                    "good_threshold": self.quality_thresholds.good_threshold,
                    "acceptable_threshold": self.quality_thresholds.acceptable_threshold,
                    "poor_threshold": self.quality_thresholds.poor_threshold,
                    "min_snr_db": self.quality_thresholds.min_snr_db,
                    "max_thd_percent": self.quality_thresholds.max_thd_percent,
                    "min_dynamic_range_db": self.quality_thresholds.min_dynamic_range_db
                },
                "perceptual_config": {
                    "enable_psychoacoustic_model": self.perceptual_config.enable_psychoacoustic_model,
                    "use_bark_scale": self.perceptual_config.use_bark_scale,
                    "masking_threshold_analysis": self.perceptual_config.masking_threshold_analysis,
                    "loudness_weighting": self.perceptual_config.loudness_weighting
                },
                "technical_config": {
                    "analyze_frequency_response": self.technical_config.analyze_frequency_response,
                    "analyze_phase_response": self.technical_config.analyze_phase_response,
                    "analyze_harmonic_distortion": self.technical_config.analyze_harmonic_distortion,
                    "analyze_dynamic_range": self.technical_config.analyze_dynamic_range,
                    "analyze_stereo_characteristics": self.technical_config.analyze_stereo_characteristics
                },
                "enhancement_config": {
                    "enable_noise_reduction": self.enhancement_config.enable_noise_reduction,
                    "enable_dynamic_range_enhancement": self.enhancement_config.enable_dynamic_range_enhancement,
                    "enable_spectral_enhancement": self.enhancement_config.enable_spectral_enhancement,
                    "enhancement_strength": self.enhancement_config.enhancement_strength,
                    "preserve_original_character": self.enhancement_config.preserve_original_character
                },
                "standard_config": self.get_quality_standard_config(self._quality_standard)
            }
            
        except Exception as e:
            self.logger.error(f"Quality config creation failed: {e}")
            return {"error": str(e)}
    
    def validate_quality_requirements(self, 
                                    metrics: Dict[str, float],
                                    requirements: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """        Validate audio quality against specific requirements
        
        Args:
            metrics: Audio quality metrics
            requirements: Quality requirements to validate against
            
        Returns:
            Tuple of (meets_requirements, failed_requirements)
        """        failed_requirements = []
        
        try:
            # Check minimum SNR
            if "min_snr" in requirements and QualityMetric.SNR.value in metrics:
                if metrics[QualityMetric.SNR.value] < requirements["min_snr"]:
                    failed_requirements.append(f"SNR too low: {metrics[QualityMetric.SNR.value]:.1f}dB < {requirements['min_snr']}dB")
            
            # Check maximum THD
            if "max_thd" in requirements and QualityMetric.THD.value in metrics:
                thd_percent = metrics[QualityMetric.THD.value] * 100
                if thd_percent > requirements["max_thd"]:
                    failed_requirements.append(f"THD too high: {thd_percent:.2f}% > {requirements['max_thd']}%")
            
            # Check loudness range
            if "lufs_range" in requirements and QualityMetric.LOUDNESS_LUFS.value in metrics:
                min_lufs, max_lufs = requirements["lufs_range"]
                actual_lufs = metrics[QualityMetric.LOUDNESS_LUFS.value]
                if not (min_lufs <= actual_lufs <= max_lufs):
                    failed_requirements.append(f"Loudness out of range: {actual_lufs:.1f} LUFS not in [{min_lufs}, {max_lufs}]")
            
            # Check peak level
            if "max_peak" in requirements and QualityMetric.PEAK_LEVEL.value in metrics:
                if metrics[QualityMetric.PEAK_LEVEL.value] > requirements["max_peak"]:
                    failed_requirements.append(f"Peak level too high: {metrics[QualityMetric.PEAK_LEVEL.value]:.1f}dBFS > {requirements['max_peak']}dBFS")
            
            # Check minimum dynamic range
            if "min_dynamic_range" in requirements and QualityMetric.DYNAMIC_RANGE.value in metrics:
                if metrics[QualityMetric.DYNAMIC_RANGE.value] < requirements["min_dynamic_range"]:
                    failed_requirements.append(f"Dynamic range too low: {metrics[QualityMetric.DYNAMIC_RANGE.value]:.1f}dB < {requirements['min_dynamic_range']}dB")
            
        except Exception as e:
            failed_requirements.append(f"Validation error: {str(e)}")
        
        meets_requirements = len(failed_requirements) == 0
        return meets_requirements, failed_requirements
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete audio quality configuration"""        try:
            return {
                "quality_standard": self._quality_standard.value,
                "analysis_depth": self._analysis_depth.value,
                "target_grade": self._target_grade.value,
                "enabled_metrics": [metric.value for metric in self._enabled_metrics],
                "metric_weights": {metric.value: weight for metric, weight in self._metric_weights.items()},
                "quality_thresholds": {
                    "excellent_threshold": self.quality_thresholds.excellent_threshold,
                    "good_threshold": self.quality_thresholds.good_threshold,
                    "acceptable_threshold": self.quality_thresholds.acceptable_threshold,
                    "poor_threshold": self.quality_thresholds.poor_threshold,
                    "min_snr_db": self.quality_thresholds.min_snr_db,
                    "max_thd_percent": self.quality_thresholds.max_thd_percent,
                    "min_dynamic_range_db": self.quality_thresholds.min_dynamic_range_db,
                    "max_peak_lufs": self.quality_thresholds.max_peak_lufs,
                    "min_loudness_lufs": self.quality_thresholds.min_loudness_lufs,
                    "max_loudness_lufs": self.quality_thresholds.max_loudness_lufs
                },
                "perceptual_config": {
                    "enable_psychoacoustic_model": self.perceptual_config.enable_psychoacoustic_model,
                    "use_bark_scale": self.perceptual_config.use_bark_scale,
                    "use_critical_bands": self.perceptual_config.use_critical_bands,
                    "masking_threshold_analysis": self.perceptual_config.masking_threshold_analysis,
                    "temporal_masking": self.perceptual_config.temporal_masking,
                    "frequency_masking": self.perceptual_config.frequency_masking,
                    "loudness_weighting": self.perceptual_config.loudness_weighting
                },
                "technical_config": {
                    "analyze_frequency_response": self.technical_config.analyze_frequency_response,
                    "analyze_phase_response": self.technical_config.analyze_phase_response,
                    "analyze_harmonic_distortion": self.technical_config.analyze_harmonic_distortion,
                    "analyze_intermodulation": self.technical_config.analyze_intermodulation,
                    "analyze_noise_spectrum": self.technical_config.analyze_noise_spectrum,
                    "analyze_dynamic_range": self.technical_config.analyze_dynamic_range,
                    "analyze_stereo_characteristics": self.technical_config.analyze_stereo_characteristics
                },
                "enhancement_config": {
                    "enable_noise_reduction": self.enhancement_config.enable_noise_reduction,
                    "enable_dynamic_range_enhancement": self.enhancement_config.enable_dynamic_range_enhancement,
                    "enable_spectral_enhancement": self.enhancement_config.enable_spectral_enhancement,
                    "enable_stereo_enhancement": self.enhancement_config.enable_stereo_enhancement,
                    "enable_harmonic_enhancement": self.enhancement_config.enable_harmonic_enhancement,
                    "enhancement_strength": self.enhancement_config.enhancement_strength,
                    "preserve_original_character": self.enhancement_config.preserve_original_character
                },
                "standard_configs": {
                    standard.value: config for standard, config in self._standard_configs.items()
                },
                "quality_profiles": self._quality_profiles
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
