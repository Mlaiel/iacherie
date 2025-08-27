"""
Audio Enhancement Events - Industrial Grade Audio Enhancement & Mastering
========================================================================

This module handles all events related to audio enhancement, mastering,
noise reduction, and quality improvement processes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class EnhancementType(Enum):
    """Types of audio enhancement"""
    NOISE_REDUCTION = "noise_reduction"
    MASTERING = "mastering"
    RESTORATION = "restoration"
    SPATIAL_ENHANCEMENT = "spatial_enhancement"
    DYNAMIC_ENHANCEMENT = "dynamic_enhancement"
    FREQUENCY_ENHANCEMENT = "frequency_enhancement"
    STEREO_WIDENING = "stereo_widening"
    HARMONIC_ENHANCEMENT = "harmonic_enhancement"
    VOCAL_ENHANCEMENT = "vocal_enhancement"
    INSTRUMENTAL_ENHANCEMENT = "instrumental_enhancement"


class NoiseType(Enum):
    """Types of noise to be reduced"""
    BACKGROUND_NOISE = "background_noise"
    HISS = "hiss"
    HUM = "hum"
    CLICKS_POPS = "clicks_pops"
    DIGITAL_ARTIFACTS = "digital_artifacts"
    WIND_NOISE = "wind_noise"
    ROOM_TONE = "room_tone"
    ELECTRICAL_INTERFERENCE = "electrical_interference"
    COMPRESSION_ARTIFACTS = "compression_artifacts"
    MICROPHONE_HANDLING = "microphone_handling"


class MasteringPreset(Enum):
    """Mastering presets for different purposes"""
    STREAMING = "streaming"
    CD_RELEASE = "cd_release"
    VINYL = "vinyl"
    RADIO = "radio"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    FILM_SCORE = "film_score"
    COMMERCIAL = "commercial"
    LIVE_RECORDING = "live_recording"
    CUSTOM = "custom"


@dataclass
class AudioEnhancementStartedEvent(BaseEvent):
    """
    Event triggered when audio enhancement process begins.
    
    Initializes comprehensive audio enhancement pipeline with AI-powered
    analysis and processing algorithms.
    """
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    filename: str
    enhancement_types: List[EnhancementType]
    enhancement_preset: str
    quality_target: str  # broadcast, studio, audiophile, streaming
    ai_enhancement_enabled: bool
    real_time_processing: bool
    preserve_dynamics: bool
    preserve_character: bool
    estimated_duration: float
    processing_priority: int
    hardware_acceleration: bool
    reference_track_id: Optional[UUID] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.started",
            event_category=EventCategory.ENHANCEMENT,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "enhancement_types_count": len(self.enhancement_types),
                "quality_target": self.quality_target,
                "ai_enhanced": self.ai_enhancement_enabled,
                "estimated_duration": self.estimated_duration
            }
        )


@dataclass
class AudioEnhancementProgressEvent(BaseEvent):
    """
    Event triggered during audio enhancement progress updates.
    
    Provides real-time feedback about enhancement pipeline progress.
    """
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    current_enhancement_type: EnhancementType
    enhancement_progress: float  # 0.0 to 1.0
    overall_progress: float  # 0.0 to 1.0
    elapsed_time: float
    estimated_remaining: float
    current_operation: str
    quality_improvement: float
    artifacts_detected: int
    artifacts_corrected: int
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.progress",
            event_category=EventCategory.ENHANCEMENT,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "current_enhancement": self.current_enhancement_type.value,
                "overall_progress": self.overall_progress,
                "quality_improvement": self.quality_improvement
            }
        )


@dataclass
class AudioEnhancementCompletedEvent(BaseEvent):
    """
    Event triggered when audio enhancement is successfully completed.
    
    Contains comprehensive enhancement results and quality metrics.
    """
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    enhanced_file_id: UUID
    original_filename: str
    enhanced_filename: str
    enhancement_duration: float
    enhancements_applied: List[str]
    quality_improvement_metrics: Dict[str, float]
    before_after_comparison: Dict[str, Any]
    artifacts_removed: int
    noise_reduction_db: float
    dynamic_range_improvement: float
    frequency_response_improvement: Dict[str, float]
    overall_quality_score: float
    enhancement_settings: Dict[str, Any]
    preservation_score: float  # how well original character was preserved
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.completed",
            event_category=EventCategory.ENHANCEMENT,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "enhanced_file_id": str(self.enhanced_file_id),
                "enhancement_duration": self.enhancement_duration,
                "quality_score": self.overall_quality_score,
                "enhancements_count": len(self.enhancements_applied)
            }
        )


@dataclass
class AudioEnhancementFailedEvent(BaseEvent):
    """
    Event triggered when audio enhancement fails.
    
    Contains detailed error information and recovery options.
    """
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    failed_enhancement_type: EnhancementType
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    enhancement_duration: float
    enhancements_completed: List[str]
    partial_results: Dict[str, Any]
    retry_count: int
    max_retries: int
    is_retryable: bool
    fallback_methods_available: List[str]
    suggested_action: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.failed",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "failed_enhancement": self.failed_enhancement_type.value,
                "error_code": self.error_code,
                "retry_count": self.retry_count,
                "has_partial_results": len(self.partial_results) > 0
            }
        )


@dataclass
class AudioNoiseReductionEvent(BaseEvent):
    """
    Event triggered when noise reduction process is completed.
    
    Contains detailed noise analysis and reduction results.
    """
    user_id: UUID
    file_id: UUID
    reduction_id: UUID
    noise_types_detected: List[NoiseType]
    noise_levels_before: Dict[str, float]  # noise type -> level in dB
    noise_levels_after: Dict[str, float]
    noise_reduction_db: Dict[str, float]  # per noise type
    overall_noise_reduction: float
    signal_preservation: float
    artifacts_introduced: int
    noise_profile_learned: bool
    spectral_subtraction_used: bool
    adaptive_filtering_used: bool
    ai_denoising_used: bool
    processing_quality: str  # conservative, balanced, aggressive
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.noise_reduction",
            event_category=EventCategory.NOISE_REDUCTION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "reduction_id": str(self.reduction_id),
                "noise_types_count": len(self.noise_types_detected),
                "overall_reduction_db": self.overall_noise_reduction,
                "signal_preservation": self.signal_preservation,
                "ai_denoising": self.ai_denoising_used
            }
        )


@dataclass
class AudioMasteringEvent(BaseEvent):
    """
    Event triggered when mastering process is completed.
    
    Contains comprehensive mastering analysis and processing results.
    """
    user_id: UUID
    file_id: UUID
    mastering_id: UUID
    mastering_preset: MasteringPreset
    target_loudness_lufs: float
    achieved_loudness_lufs: float
    dynamic_range_dr: float
    peak_level_dbfs: float
    rms_level_dbfs: float
    true_peak_dbtp: float
    eq_applied: Dict[str, float]  # frequency -> gain
    compression_applied: Dict[str, Any]
    limiting_applied: Dict[str, Any]
    stereo_enhancement: Dict[str, Any]
    harmonic_enhancement: Dict[str, Any]
    frequency_spectrum_before: List[float]
    frequency_spectrum_after: List[float]
    mastering_quality_score: float
    reference_matching_score: Optional[float] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.mastering",
            event_category=EventCategory.MASTERING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "mastering_id": str(self.mastering_id),
                "preset": self.mastering_preset.value,
                "target_lufs": self.target_loudness_lufs,
                "achieved_lufs": self.achieved_loudness_lufs,
                "dynamic_range": self.dynamic_range_dr,
                "quality_score": self.mastering_quality_score
            }
        )


@dataclass
class AudioRestorationEvent(BaseEvent):
    """
    Event triggered when audio restoration process is completed.
    
    Handles restoration of degraded or damaged audio recordings.
    """
    user_id: UUID
    file_id: UUID
    restoration_id: UUID
    degradation_types: List[str]
    restoration_techniques: List[str]
    quality_before: float
    quality_after: float
    restoration_success_rate: float
    clicks_removed: int
    pops_removed: int
    dropouts_repaired: int
    wow_flutter_corrected: bool
    speed_variations_corrected: bool
    frequency_response_restored: bool
    dynamic_range_restored: float
    spectral_repair_applied: bool
    interpolation_methods_used: List[str]
    ai_restoration_confidence: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.restoration",
            event_category=EventCategory.RESTORATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "restoration_id": str(self.restoration_id),
                "degradation_types_count": len(self.degradation_types),
                "quality_improvement": self.quality_after - self.quality_before,
                "success_rate": self.restoration_success_rate,
                "ai_confidence": self.ai_restoration_confidence
            }
        )


@dataclass
class AudioSpatialEnhancementEvent(BaseEvent):
    """
    Event triggered when spatial enhancement is completed.
    
    Handles stereo widening, surround sound, and 3D audio processing.
    """
    user_id: UUID
    file_id: UUID
    spatial_id: UUID
    spatial_format: str  # stereo, 5.1, 7.1, binaural, ambisonic
    stereo_width_original: float
    stereo_width_enhanced: float
    spatial_imaging_score: float
    phase_coherence: float
    center_channel_balance: float
    surround_field_quality: float
    height_information_added: bool
    binaural_processing_applied: bool
    room_simulation_applied: bool
    head_tracking_enabled: bool
    spatial_resolution: str  # low, medium, high, ultra
    immersion_level: float
    localization_accuracy: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.spatial",
            event_category=EventCategory.SPATIAL,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "spatial_id": str(self.spatial_id),
                "spatial_format": self.spatial_format,
                "stereo_width_gain": self.stereo_width_enhanced - self.stereo_width_original,
                "imaging_score": self.spatial_imaging_score,
                "immersion_level": self.immersion_level
            }
        )


@dataclass
class AudioVocalEnhancementEvent(BaseEvent):
    """
    Event triggered when vocal enhancement is completed.
    
    Specialized enhancement for vocal recordings and performances.
    """
    user_id: UUID
    file_id: UUID
    vocal_enhancement_id: UUID
    vocal_clarity_improvement: float
    presence_enhancement: float
    warmth_adjustment: float
    breath_noise_reduction: float
    sibilance_control: float
    vocal_dynamics_optimization: bool
    pitch_correction_applied: bool
    timing_correction_applied: bool
    vocal_doubling_created: bool
    harmony_enhancement: bool
    vocal_effects_applied: List[str]
    formant_correction: bool
    vocal_character_preservation: float
    intelligibility_improvement: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.enhancement.vocal",
            event_category=EventCategory.VOCAL,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "vocal_enhancement_id": str(self.vocal_enhancement_id),
                "clarity_improvement": self.vocal_clarity_improvement,
                "presence_enhancement": self.presence_enhancement,
                "character_preservation": self.vocal_character_preservation,
                "effects_count": len(self.vocal_effects_applied)
            }
        )
