"""
Audio Analysis Events - Industrial Grade AI Analysis & Music Intelligence
========================================================================

This module handles all events related to advanced audio analysis including
genre detection, mood analysis, BPM detection, and AI-powered music intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class AnalysisType(Enum):
    """Types of audio analysis"""
    GENRE_DETECTION = "genre_detection"
    MOOD_ANALYSIS = "mood_analysis"
    BPM_DETECTION = "bpm_detection"
    KEY_DETECTION = "key_detection"
    INSTRUMENT_RECOGNITION = "instrument_recognition"
    VOCAL_ANALYSIS = "vocal_analysis"
    STRUCTURE_ANALYSIS = "structure_analysis"
    EMOTION_DETECTION = "emotion_detection"
    ENERGY_ANALYSIS = "energy_analysis"
    DANCEABILITY = "danceability"


class MusicalKey(Enum):
    """Musical keys"""
    C_MAJOR = "C major"
    C_SHARP_MAJOR = "C# major"
    D_MAJOR = "D major"
    D_SHARP_MAJOR = "D# major"
    E_MAJOR = "E major"
    F_MAJOR = "F major"
    F_SHARP_MAJOR = "F# major"
    G_MAJOR = "G major"
    G_SHARP_MAJOR = "G# major"
    A_MAJOR = "A major"
    A_SHARP_MAJOR = "A# major"
    B_MAJOR = "B major"
    C_MINOR = "C minor"
    C_SHARP_MINOR = "C# minor"
    D_MINOR = "D minor"
    D_SHARP_MINOR = "D# minor"
    E_MINOR = "E minor"
    F_MINOR = "F minor"
    F_SHARP_MINOR = "F# minor"
    G_MINOR = "G minor"
    G_SHARP_MINOR = "G# minor"
    A_MINOR = "A minor"
    A_SHARP_MINOR = "A# minor"
    B_MINOR = "B minor"


class TimeSignature(Enum):
    """Common time signatures"""
    FOUR_FOUR = "4/4"
    THREE_FOUR = "3/4"
    TWO_FOUR = "2/4"
    SIX_EIGHT = "6/8"
    NINE_EIGHT = "9/8"
    TWELVE_EIGHT = "12/8"
    FIVE_FOUR = "5/4"
    SEVEN_EIGHT = "7/8"


@dataclass
class AudioAnalysisStartedEvent(BaseEvent):
    """
    Event triggered when comprehensive audio analysis begins.
    
    Initializes AI-powered music intelligence analysis pipeline.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    analysis_types: List[AnalysisType]
    ai_models_enabled: List[str]
    analysis_depth: str  # quick, standard, deep, comprehensive
    priority_level: int
    estimated_duration: float
    segment_analysis: bool
    real_time_processing: bool
    gpu_acceleration: bool
    model_versions: Dict[str, str]
    analysis_parameters: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.started",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "analysis_types_count": len(self.analysis_types),
                "analysis_depth": self.analysis_depth,
                "estimated_duration": self.estimated_duration,
                "gpu_acceleration": self.gpu_acceleration
            }
        )


@dataclass
class AudioAnalysisProgressEvent(BaseEvent):
    """
    Event triggered during audio analysis progress updates.
    
    Provides real-time feedback about AI analysis pipeline progress.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    current_analysis_type: AnalysisType
    analysis_progress: float  # 0.0 to 1.0
    overall_progress: float  # 0.0 to 1.0
    elapsed_time: float
    estimated_remaining: float
    current_model: str
    segments_analyzed: int
    total_segments: int
    intermediate_results: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.progress",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "current_analysis": self.current_analysis_type.value,
                "overall_progress": self.overall_progress,
                "estimated_remaining": self.estimated_remaining
            }
        )


@dataclass
class AudioAnalysisCompletedEvent(BaseEvent):
    """
    Event triggered when comprehensive audio analysis is completed.
    
    Contains all analysis results and AI-generated insights.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    analysis_duration: float
    analysis_results: Dict[str, Any]
    confidence_scores: Dict[str, float]
    ai_insights: List[str]
    recommendations: List[str]
    comparable_tracks: List[Dict[str, Any]]
    analysis_quality: float
    models_used: List[str]
    processing_statistics: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.completed",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "analysis_duration": self.analysis_duration,
                "insights_count": len(self.ai_insights),
                "recommendations_count": len(self.recommendations),
                "analysis_quality": self.analysis_quality
            }
        )


@dataclass
class AudioAnalysisFailedEvent(BaseEvent):
    """
    Event triggered when audio analysis fails.
    
    Contains detailed error information and recovery options.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    failed_analysis_type: AnalysisType
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    partial_results: Dict[str, Any]
    analysis_duration: float
    retry_count: int
    max_retries: int
    is_retryable: bool
    fallback_models_available: List[str]
    suggested_action: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.failed",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "failed_analysis": self.failed_analysis_type.value,
                "error_code": self.error_code,
                "retry_count": self.retry_count,
                "has_partial_results": len(self.partial_results) > 0
            }
        )


@dataclass
class AudioGenreDetectionEvent(BaseEvent):
    """
    Event triggered when genre detection analysis is completed.
    
    Contains detailed genre classification and confidence scores.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    primary_genre: str
    secondary_genres: List[Tuple[str, float]]  # (genre, confidence)
    genre_confidence: float
    subgenre_detected: Optional[str] = None
    genre_fusion: List[str] = field(default_factory=list)
    genre_evolution_timeline: List[Tuple[float, str]] = field(default_factory=list)
    cultural_influence: List[str] = field(default_factory=list)
    tempo_genre_correlation: float
    harmonic_genre_markers: List[str]
    rhythmic_genre_markers: List[str]
    instrumental_genre_markers: List[str]
    vocal_genre_markers: List[str]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.genre_detection",
            event_category=EventCategory.CLASSIFICATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "primary_genre": self.primary_genre,
                "genre_confidence": self.genre_confidence,
                "secondary_genres_count": len(self.secondary_genres),
                "subgenre_detected": self.subgenre_detected
            }
        )


@dataclass
class AudioMoodAnalysisEvent(BaseEvent):
    """
    Event triggered when mood analysis is completed.
    
    Contains emotional and atmospheric analysis results.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    primary_mood: str
    mood_confidence: float
    emotional_valence: float  # -1.0 (negative) to 1.0 (positive)
    emotional_arousal: float  # 0.0 (calm) to 1.0 (energetic)
    mood_progression: List[Tuple[float, str, float]]  # (time, mood, confidence)
    emotional_intensity: float
    mood_stability: float
    atmospheric_qualities: List[str]
    listener_emotions: List[str]
    contextual_mood: Dict[str, float]  # situational appropriateness
    mood_keywords: List[str]
    color_associations: List[str]
    weather_associations: List[str]
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.mood_analysis",
            event_category=EventCategory.CLASSIFICATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "primary_mood": self.primary_mood,
                "mood_confidence": self.mood_confidence,
                "emotional_valence": self.emotional_valence,
                "emotional_arousal": self.emotional_arousal,
                "mood_stability": self.mood_stability
            }
        )


@dataclass
class AudioBPMDetectionEvent(BaseEvent):
    """
    Event triggered when BPM (tempo) detection is completed.
    
    Contains detailed tempo analysis and rhythmic information.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    bpm: float
    bpm_confidence: float
    tempo_stability: float
    time_signature: TimeSignature
    time_signature_confidence: float
    tempo_variations: List[Tuple[float, float]]  # (time, bpm)
    rhythmic_complexity: float
    beat_strength: List[float]  # per beat strength
    downbeat_positions: List[float]
    measure_positions: List[float]
    rhythm_pattern: str
    swing_factor: float
    groove_feel: str
    percussion_prominence: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.bpm_detection",
            event_category=EventCategory.RHYTHM,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "bpm": self.bpm,
                "bpm_confidence": self.bpm_confidence,
                "time_signature": self.time_signature.value,
                "tempo_stability": self.tempo_stability,
                "rhythmic_complexity": self.rhythmic_complexity
            }
        )


@dataclass
class AudioKeyDetectionEvent(BaseEvent):
    """
    Event triggered when musical key detection is completed.
    
    Contains harmonic analysis and key progression information.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    musical_key: MusicalKey
    key_confidence: float
    mode: str  # major, minor, dorian, etc.
    key_stability: float
    key_changes: List[Tuple[float, MusicalKey, float]]  # (time, key, confidence)
    harmonic_complexity: float
    chord_progression: List[Tuple[float, str]]  # (time, chord)
    scale_degrees: List[float]
    tonal_center_strength: float
    modulation_points: List[float]
    relative_keys: List[Tuple[MusicalKey, float]]
    harmonic_rhythm: float
    consonance_level: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.key_detection",
            event_category=EventCategory.HARMONY,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "musical_key": self.musical_key.value,
                "key_confidence": self.key_confidence,
                "mode": self.mode,
                "key_stability": self.key_stability,
                "harmonic_complexity": self.harmonic_complexity
            }
        )


@dataclass
class AudioInstrumentRecognitionEvent(BaseEvent):
    """
    Event triggered when instrument recognition is completed.
    
    Contains detailed information about detected instruments.
    """
    user_id: UUID
    file_id: UUID
    recognition_id: UUID
    detected_instruments: List[Tuple[str, float, float, float]]  # (instrument, confidence, start, end)
    instrument_families: List[str]
    lead_instrument: Optional[str] = None
    rhythm_section: List[str] = field(default_factory=list)
    orchestral_arrangement: bool = False
    acoustic_vs_electric: Dict[str, str]
    instrument_quality: Dict[str, float]
    playing_techniques: Dict[str, List[str]]
    ensemble_size: str  # solo, duo, trio, quartet, band, orchestra
    arrangement_density: float
    instrument_interactions: List[Tuple[str, str, str]]  # (inst1, inst2, interaction_type)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.instrument_recognition",
            event_category=EventCategory.CLASSIFICATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "recognition_id": str(self.recognition_id),
                "instruments_count": len(self.detected_instruments),
                "lead_instrument": self.lead_instrument,
                "ensemble_size": self.ensemble_size,
                "orchestral": self.orchestral_arrangement
            }
        )


@dataclass
class AudioVocalAnalysisEvent(BaseEvent):
    """
    Event triggered when vocal analysis is completed.
    
    Contains detailed vocal performance and characteristics analysis.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    vocals_detected: bool
    vocal_segments: List[Tuple[float, float]]  # (start, end)
    vocal_quality: float
    vocal_range: Tuple[float, float]  # (lowest_hz, highest_hz)
    vocal_style: str
    vocal_technique: List[str]
    gender_prediction: str
    age_estimation: Tuple[int, int]  # (min_age, max_age)
    vocal_emotion: str
    vocal_energy: float
    vibrato_detected: bool
    vocal_effects: List[str]
    harmony_vocals: bool
    background_vocals: bool
    vocal_clarity: float
    pronunciation_quality: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.vocal_analysis",
            event_category=EventCategory.CLASSIFICATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "vocals_detected": self.vocals_detected,
                "vocal_quality": self.vocal_quality,
                "vocal_style": self.vocal_style,
                "vocal_segments_count": len(self.vocal_segments)
            }
        )
