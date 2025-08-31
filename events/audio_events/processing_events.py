"""Audio Processing Events - Industrial Grade Processing Event Management
====================================================================

This module handles all events related to audio processing including quality analysis,
format conversion, enhancement, and real-time processing pipelines.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class ProcessingStage(Enum):
    """Audio processing pipeline stages"""    INITIALIZATION = "initialization"
    FORMAT_CONVERSION = "format_conversion"
    QUALITY_ANALYSIS = "quality_analysis"
    ENHANCEMENT = "enhancement"
    COMPRESSION = "compression"
    NORMALIZATION = "normalization"
    FILTERING = "filtering"
    FINALIZATION = "finalization"


class ProcessingQuality(Enum):
    """Audio processing quality levels"""    LOSSLESS = "lossless"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STREAMING = "streaming"


@dataclass
class AudioProcessingStartedEvent(BaseEvent):
    """    Event triggered when audio processing pipeline begins.
    
    Initializes comprehensive audio processing including analysis,
    enhancement, and optimization workflows.
    """    user_id: UUID
    file_id: UUID
    processing_id: UUID
    filename: str
    processing_type: str  # enhancement, conversion, analysis, optimization
    processing_stages: List[str]
    quality_target: ProcessingQuality
    priority_level: int
    estimated_duration: float
    processing_parameters: Dict[str, Any]
    hardware_allocation: Dict[str, Any]
    cpu_cores_allocated: int
    memory_allocated: int  # MB
    gpu_enabled: bool = False
    parallel_processing: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.started",
            event_category=EventCategory.PROCESSING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "processing_type": self.processing_type,
                "stages_count": len(self.processing_stages),
                "quality_target": self.quality_target.value,
                "estimated_duration": self.estimated_duration,
                "cpu_cores": self.cpu_cores_allocated,
                "memory_mb": self.memory_allocated,
                "gpu_enabled": self.gpu_enabled
            }
        )


@dataclass
class AudioProcessingProgressEvent(BaseEvent):
    """    Event triggered during audio processing progress updates.
    
    Provides real-time feedback about processing pipeline progress.
    """    user_id: UUID
    file_id: UUID
    processing_id: UUID
    current_stage: ProcessingStage
    stage_progress: float  # 0.0 to 1.0
    overall_progress: float  # 0.0 to 1.0
    elapsed_time: float
    estimated_remaining: float
    current_operation: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None
    throughput: float = 0.0  # samples per second
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.progress",
            event_category=EventCategory.PROCESSING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "current_stage": self.current_stage.value,
                "overall_progress": self.overall_progress,
                "estimated_remaining": self.estimated_remaining,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage
            }
        )


@dataclass
class AudioProcessingCompletedEvent(BaseEvent):
    """    Event triggered when audio processing is successfully completed.
    
    Contains comprehensive results and metrics from the processing pipeline.
    """    user_id: UUID
    file_id: UUID
    processing_id: UUID
    processed_file_id: UUID
    original_filename: str
    processed_filename: str
    processing_duration: float
    processing_stages_completed: List[str]
    processing_results: Dict[str, Any]
    quality_metrics: Dict[str, float]
    file_size_original: int
    file_size_processed: int
    compression_ratio: float
    quality_improvement: Dict[str, float]
    output_formats: List[str]
    storage_locations: Dict[str, str]
    checksum_original: str
    checksum_processed: str
    metadata_preserved: bool
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.completed",
            event_category=EventCategory.PROCESSING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "processed_file_id": str(self.processed_file_id),
                "processing_duration": self.processing_duration,
                "stages_completed": len(self.processing_stages_completed),
                "compression_ratio": self.compression_ratio,
                "output_formats_count": len(self.output_formats)
            }
        )


@dataclass
class AudioProcessingFailedEvent(BaseEvent):
    """    Event triggered when audio processing fails.
    
    Contains detailed error information and recovery options.
    """    user_id: UUID
    file_id: UUID
    processing_id: UUID
    failed_stage: ProcessingStage
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    stack_trace: Optional[str] = None
    processing_duration: float
    stages_completed: List[str]
    stages_failed: List[str]
    retry_count: int
    max_retries: int
    is_retryable: bool
    suggested_action: str
    hardware_usage: Dict[str, float]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.failed",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "failed_stage": self.failed_stage.value,
                "error_code": self.error_code,
                "retry_count": self.retry_count,
                "is_retryable": self.is_retryable
            }
        )


@dataclass
class AudioQualityAnalysisEvent(BaseEvent):
    """    Event triggered when audio quality analysis is completed.
    
    Contains comprehensive quality metrics and recommendations.
    """    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    quality_score: float  # 0.0 to 1.0
    dynamic_range: float
    signal_to_noise_ratio: float
    frequency_response: Dict[str, float]
    harmonic_distortion: float
    peak_level: float
    rms_level: float
    loudness_lufs: float
    clipping_detected: bool
    clipping_count: int
    noise_floor: float
    stereo_width: float
    phase_correlation: float
    quality_issues: List[Dict[str, Any]]
    recommendations: List[str]
    comparable_references: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.quality_analysis",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "quality_score": self.quality_score,
                "snr": self.signal_to_noise_ratio,
                "dynamic_range": self.dynamic_range,
                "clipping_detected": self.clipping_detected,
                "issues_count": len(self.quality_issues),
                "recommendations_count": len(self.recommendations)
            }
        )


@dataclass
class AudioFormatConversionEvent(BaseEvent):
    """    Event triggered during audio format conversion process.
    
    Handles conversion between different audio formats and quality levels.
    """    user_id: UUID
    file_id: UUID
    conversion_id: UUID
    source_format: str
    target_format: str
    source_sample_rate: int
    target_sample_rate: int
    source_bit_depth: int
    target_bit_depth: int
    source_channels: int
    target_channels: int
    conversion_method: str
    quality_preset: str
    conversion_parameters: Dict[str, Any]
    estimated_quality_loss: float
    file_size_change: float
    conversion_duration: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.format_conversion",
            event_category=EventCategory.CONVERSION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "conversion_id": str(self.conversion_id),
                "source_format": self.source_format,
                "target_format": self.target_format,
                "sample_rate_change": f"{self.source_sample_rate}->{self.target_sample_rate}",
                "bit_depth_change": f"{self.source_bit_depth}->{self.target_bit_depth}",
                "estimated_quality_loss": self.estimated_quality_loss
            }
        )


@dataclass
class AudioNormalizationEvent(BaseEvent):
    """    Event triggered during audio normalization process.
    
    Handles loudness normalization and level optimization.
    """    user_id: UUID
    file_id: UUID
    normalization_id: UUID
    normalization_type: str  # peak, rms, lufs, ebu_r128
    target_level: float
    original_peak: float
    original_rms: float
    original_lufs: float
    normalized_peak: float
    normalized_rms: float
    normalized_lufs: float
    gain_applied: float
    dynamic_range_preserved: bool
    limiting_applied: bool
    normalization_quality: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.normalization",
            event_category=EventCategory.ENHANCEMENT,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "normalization_id": str(self.normalization_id),
                "normalization_type": self.normalization_type,
                "gain_applied": self.gain_applied,
                "target_level": self.target_level,
                "quality": self.normalization_quality
            }
        )


@dataclass
class AudioCompressionEvent(BaseEvent):
    """    Event triggered during audio compression process.
    
    Handles dynamic range compression and limiting.
    """    user_id: UUID
    file_id: UUID
    compression_id: UUID
    compressor_type: str  # vca, optical, tube, digital
    threshold: float
    ratio: float
    attack_time: float
    release_time: float
    knee_width: float
    makeup_gain: float
    compression_amount: float
    original_dynamic_range: float
    compressed_dynamic_range: float
    perceived_loudness_change: float
    transparency_score: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.compression",
            event_category=EventCategory.ENHANCEMENT,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "compression_id": str(self.compression_id),
                "compressor_type": self.compressor_type,
                "ratio": self.ratio,
                "compression_amount": self.compression_amount,
                "transparency_score": self.transparency_score
            }
        )


@dataclass
class AudioSpectrumAnalysisEvent(BaseEvent):
    """    Event triggered when spectral analysis is completed.
    
    Contains detailed frequency domain analysis results.
    """    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    spectrum_data: Dict[str, List[float]]
    frequency_bins: List[float]
    magnitude_spectrum: List[float]
    phase_spectrum: List[float]
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    spectral_flatness: float
    zero_crossing_rate: float
    fundamental_frequency: float
    harmonics: List[Tuple[float, float]]  # (frequency, magnitude)
    formants: List[float]
    spectral_peaks: List[Tuple[float, float]]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.spectrum_analysis",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.LOW,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "spectral_centroid": self.spectral_centroid,
                "fundamental_frequency": self.fundamental_frequency,
                "harmonics_count": len(self.harmonics),
                "formants_count": len(self.formants)
            }
        )
