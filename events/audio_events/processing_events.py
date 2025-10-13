"""Audio Processing Events - Industrial Grade Processing Event Management
====================================================================

This module handles all events related to audio processing including quality analysis,
format conversion, enhancement, and real-time processing pipelines.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, modification, or distribution of this code is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class ProcessingStage(Enum):
    """Audio processing pipeline stages"""
    INITIALIZATION = "initialization"
    FORMAT_CONVERSION = "format_conversion"
    QUALITY_ANALYSIS = "quality_analysis"
    ENHANCEMENT = "enhancement"
    COMPRESSION = "compression"
    NORMALIZATION = "normalization"
    FILTERING = "filtering"
    FINALIZATION = "finalization"


class ProcessingQuality(Enum):
    """Audio processing quality levels"""
    LOSSLESS = "lossless"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STREAMING = "streaming"


@dataclass
class AudioProcessingStartedEvent(BaseEvent):
    """
    Event triggered when audio processing pipeline begins.
    
    Initializes comprehensive audio processing including analysis,
    enhancement, and optimization workflows.
    """
    user_id: UUID
    file_id: UUID
    processing_id: UUID
    filename: str
    processing_profile: str
    input_format: str
    target_format: str
    quality_level: str
    processing_stages: List[str]
    estimated_duration: float
    processing_priority: str = "normal"
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.started",
            data={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "processing_profile": self.processing_profile,
                "input_format": self.input_format,
                "target_format": self.target_format,
                "quality_level": self.quality_level,
                "stages_count": len(self.processing_stages)
            }
        )


@dataclass
class AudioProcessingProgressEvent(BaseEvent):
    """
    Event triggered during audio processing progress updates.
    
    Provides real-time progress information for long-running processing tasks.
    """
    user_id: UUID
    file_id: UUID
    processing_id: UUID
    current_stage: str
    progress_percentage: float
    time_elapsed: float
    estimated_time_remaining: float
    current_operation: str
    stages_completed: List[str]
    stages_remaining: List[str]
    processing_speed: float = 0.0
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.progress",
            data={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "current_stage": self.current_stage,
                "progress_percentage": self.progress_percentage,
                "estimated_time_remaining": self.estimated_time_remaining
            }
        )


@dataclass
class AudioProcessingCompletedEvent(BaseEvent):
    """
    Event triggered when audio processing pipeline completes successfully.
    
    Contains comprehensive results and metrics from the processing workflow.
    """
    user_id: UUID
    file_id: UUID
    processing_id: UUID
    output_file_id: UUID
    filename: str
    output_filename: str
    processing_duration: float
    processing_stages_completed: List[str]
    quality_improvements: Dict[str, Any]
    file_size_before: int
    file_size_after: int
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.completed",
            data={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "output_file_id": str(self.output_file_id),
                "processing_duration": self.processing_duration,
                "stages_completed": len(self.processing_stages_completed),
                "size_reduction": self.file_size_before - self.file_size_after
            }
        )


@dataclass
class AudioProcessingFailedEvent(BaseEvent):
    """
    Event triggered when audio processing fails.
    
    Contains detailed error information and recovery suggestions.
    """
    user_id: UUID
    file_id: UUID
    processing_id: UUID
    filename: str
    error_code: str
    error_message: str
    failure_stage: str
    processing_duration: float
    error_details: Dict[str, Any]
    retry_suggested: bool
    alternative_profiles: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.failed",
            data={
                "file_id": str(self.file_id),
                "processing_id": str(self.processing_id),
                "error_code": self.error_code,
                "error_message": self.error_message,
                "failure_stage": self.failure_stage,
                "retry_suggested": self.retry_suggested
            }
        )


@dataclass
class AudioQualityAnalysisEvent(BaseEvent):
    """
    Event triggered when audio quality analysis is performed.
    
    Provides comprehensive quality metrics and improvement recommendations.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    overall_quality_score: float
    technical_metrics: Dict[str, Any]
    perceptual_metrics: Dict[str, Any]
    noise_analysis: Dict[str, Any]
    dynamic_range: float
    frequency_response: Dict[str, Any]
    distortion_metrics: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.quality_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "overall_quality_score": self.overall_quality_score,
                "dynamic_range": self.dynamic_range,
                "recommendations_count": len(self.recommendations)
            }
        )


@dataclass
class AudioFormatConversionEvent(BaseEvent):
    """
    Event triggered when audio format conversion is performed.
    
    Handles conversion between different audio formats and codecs.
    """
    user_id: UUID
    file_id: UUID
    conversion_id: UUID
    filename: str
    source_format: str
    target_format: str
    source_codec: str
    target_codec: str
    compression_settings: Dict[str, Any]
    conversion_duration: float
    quality_retention: float
    file_size_change: int
    conversion_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.format_conversion",
            data={
                "file_id": str(self.file_id),
                "conversion_id": str(self.conversion_id),
                "source_format": self.source_format,
                "target_format": self.target_format,
                "quality_retention": self.quality_retention,
                "conversion_duration": self.conversion_duration
            }
        )


@dataclass
class AudioAIProcessingEvent(BaseEvent):
    """
    Event triggered when AI-powered audio processing is applied.
    
    Handles machine learning based audio enhancement and analysis.
    """
    user_id: UUID
    file_id: UUID
    ai_processing_id: UUID
    filename: str
    ai_model_used: str
    processing_type: str  # enhancement, restoration, analysis, classification
    model_version: str
    confidence_score: float
    processing_results: Dict[str, Any]
    ai_suggestions: List[str]
    computational_cost: float
    ai_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.ai_processing",
            data={
                "file_id": str(self.file_id),
                "ai_processing_id": str(self.ai_processing_id),
                "ai_model_used": self.ai_model_used,
                "processing_type": self.processing_type,
                "confidence_score": self.confidence_score,
                "suggestions_count": len(self.ai_suggestions)
            }
        )


@dataclass
class AudioMLClassificationEvent(BaseEvent):
    """
    Event triggered when machine learning classification is performed.
    
    Classifies audio content using trained ML models.
    """
    user_id: UUID
    file_id: UUID
    classification_id: UUID
    filename: str
    classifier_model: str
    classification_results: Dict[str, float]
    top_prediction: str
    confidence_score: float
    feature_vector: List[float]
    model_accuracy: float
    classification_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.ml_classification",
            data={
                "file_id": str(self.file_id),
                "classification_id": str(self.classification_id),
                "classifier_model": self.classifier_model,
                "top_prediction": self.top_prediction,
                "confidence_score": self.confidence_score,
                "classes_count": len(self.classification_results)
            }
        )


@dataclass
class AudioNoiseReductionEvent(BaseEvent):
    """
    Event triggered when noise reduction processing is applied.
    
    Removes unwanted noise and artifacts from audio content.
    """
    user_id: UUID
    file_id: UUID
    noise_reduction_id: UUID
    filename: str
    noise_profile: Dict[str, Any]
    reduction_strength: float
    noise_types_detected: List[str]
    noise_reduction_db: float
    quality_preservation: float
    processing_time: float
    before_after_comparison: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.noise_reduction",
            data={
                "file_id": str(self.file_id),
                "noise_reduction_id": str(self.noise_reduction_id),
                "reduction_strength": self.reduction_strength,
                "noise_reduction_db": self.noise_reduction_db,
                "quality_preservation": self.quality_preservation,
                "noise_types_count": len(self.noise_types_detected)
            }
        )


@dataclass
class AudioBPMDetectionEvent(BaseEvent):
    """
    Event triggered when BPM (Beats Per Minute) detection is performed.
    
    Analyzes tempo and rhythm characteristics of audio content.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    detected_bpm: float
    confidence_score: float
    tempo_stability: float
    rhythm_patterns: List[Dict[str, Any]]
    time_signature: Optional[str] = None
    tempo_changes: List[Dict[str, Any]] = field(default_factory=list)
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.bpm_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "detected_bpm": self.detected_bpm,
                "confidence_score": self.confidence_score,
                "tempo_stability": self.tempo_stability,
                "tempo_changes_count": len(self.tempo_changes)
            }
        )


@dataclass
class AudioKeyDetectionEvent(BaseEvent):
    """
    Event triggered when musical key detection is performed.
    
    Identifies the musical key and tonal characteristics of audio content.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    detected_key: str
    key_confidence: float
    mode: str  # major, minor
    tonal_stability: float
    key_changes: List[Dict[str, Any]]
    harmonic_analysis: Dict[str, Any]
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.key_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "detected_key": self.detected_key,
                "key_confidence": self.key_confidence,
                "mode": self.mode,
                "tonal_stability": self.tonal_stability
            }
        )


@dataclass
class AudioGenreClassificationEvent(BaseEvent):
    """
    Event triggered when genre classification is performed.
    
    Classifies audio content into musical genres and subgenres.
    """
    user_id: UUID
    file_id: UUID
    classification_id: UUID
    filename: str
    primary_genre: str
    genre_confidence: float
    secondary_genres: List[Dict[str, float]]
    subgenre_predictions: List[Dict[str, float]]
    style_characteristics: Dict[str, Any]
    cultural_context: Optional[Dict[str, Any]] = None
    classification_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.processing.genre_classification",
            data={
                "file_id": str(self.file_id),
                "classification_id": str(self.classification_id),
                "primary_genre": self.primary_genre,
                "genre_confidence": self.genre_confidence,
                "secondary_genres_count": len(self.secondary_genres),
                "subgenres_count": len(self.subgenre_predictions)
            }
        )