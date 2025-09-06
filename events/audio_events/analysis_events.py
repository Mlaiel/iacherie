"""Audio Analysis Events - Industrial Grade Analysis Event Management
=====================================================================

This module handles all events related to audio analysis including sentiment analysis,
emotion detection, instrument recognition, and comprehensive audio analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, modification, or distribution of this code is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class AnalysisType(Enum):
    """Audio analysis types"""
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    GENRE = "genre"
    MOOD = "mood"
    INSTRUMENT = "instrument"
    VOCAL = "vocal"
    TECHNICAL = "technical"


class MusicalKey(Enum):
    """Musical key enumeration"""
    C_MAJOR = "C_major"
    C_MINOR = "C_minor"
    D_MAJOR = "D_major"
    D_MINOR = "D_minor"
    E_MAJOR = "E_major"
    E_MINOR = "E_minor"
    F_MAJOR = "F_major"
    F_MINOR = "F_minor"
    G_MAJOR = "G_major"
    G_MINOR = "G_minor"
    A_MAJOR = "A_major"
    A_MINOR = "A_minor"
    B_MAJOR = "B_major"
    B_MINOR = "B_minor"


class TimeSignature(Enum):
    """Time signature enumeration"""
    FOUR_FOUR = "4/4"
    THREE_FOUR = "3/4"
    TWO_FOUR = "2/4"
    SIX_EIGHT = "6/8"
    TWELVE_EIGHT = "12/8"


@dataclass
class AudioAnalysisStartedEvent(BaseEvent):
    """
    Event triggered when audio analysis process begins.
    
    Initializes comprehensive audio analysis workflows.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    analysis_types: List[str]
    analysis_profile: str
    estimated_duration: float
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.started",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "analysis_types": self.analysis_types,
                "analysis_profile": self.analysis_profile,
                "estimated_duration": self.estimated_duration
            }
        )


@dataclass
class AudioAnalysisProgressEvent(BaseEvent):
    """
    Event triggered during analysis progress updates.
    
    Provides real-time progress for analysis operations.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    current_analysis: str
    progress_percentage: float
    analyses_completed: List[str]
    analyses_remaining: List[str]
    estimated_time_remaining: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.progress",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "current_analysis": self.current_analysis,
                "progress_percentage": self.progress_percentage,
                "completed_count": len(self.analyses_completed)
            }
        )


@dataclass
class AudioAnalysisCompletedEvent(BaseEvent):
    """
    Event triggered when analysis process completes.
    
    Contains comprehensive analysis results and insights.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    analysis_results: Dict[str, Any]
    analysis_duration: float
    confidence_scores: Dict[str, float]
    insights_generated: List[str]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.completed",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "analysis_duration": self.analysis_duration,
                "insights_count": len(self.insights_generated),
                "results_keys": list(self.analysis_results.keys())
            }
        )


@dataclass
class AudioAnalysisFailedEvent(BaseEvent):
    """
    Event triggered when analysis process fails.
    
    Contains error information for debugging and recovery.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    error_code: str
    error_message: str
    failure_stage: str
    partial_results: Dict[str, Any] = field(default_factory=dict)
    retry_suggested: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.failed",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "error_code": self.error_code,
                "failure_stage": self.failure_stage,
                "retry_suggested": self.retry_suggested
            }
        )


@dataclass
class AudioGenreDetectionEvent(BaseEvent):
    """
    Event triggered when genre detection is completed.
    
    Identifies musical genres and subgenres of audio content.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    primary_genre: str
    genre_confidence: float
    secondary_genres: List[Dict[str, float]]
    subgenres: List[Dict[str, float]]
    genre_characteristics: Dict[str, Any]
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.genre_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "primary_genre": self.primary_genre,
                "genre_confidence": self.genre_confidence,
                "secondary_genres_count": len(self.secondary_genres)
            }
        )


@dataclass
class AudioMoodAnalysisEvent(BaseEvent):
    """
    Event triggered when mood analysis is completed.
    
    Analyzes emotional mood and atmosphere of audio content.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    primary_mood: str
    mood_confidence: float
    mood_dimensions: Dict[str, float]  # valence, arousal, dominance
    emotional_trajectory: List[Dict[str, Any]]
    mood_tags: List[str]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.mood_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "primary_mood": self.primary_mood,
                "mood_confidence": self.mood_confidence,
                "mood_tags_count": len(self.mood_tags)
            }
        )


@dataclass
class AudioBPMDetectionEvent(BaseEvent):
    """
    Event triggered when BPM detection is completed.
    
    Analyzes tempo and rhythm characteristics.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    bpm: float
    bpm_confidence: float
    tempo_stability: float
    rhythm_patterns: List[Dict[str, Any]]
    time_signature: Optional[str] = None
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.bpm_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "bpm": self.bpm,
                "bpm_confidence": self.bpm_confidence,
                "tempo_stability": self.tempo_stability
            }
        )


@dataclass
class AudioKeyDetectionEvent(BaseEvent):
    """
    Event triggered when musical key detection is completed.
    
    Identifies musical key and tonal characteristics.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    musical_key: str
    key_confidence: float
    mode: str  # major, minor
    tonal_stability: float
    key_changes: List[Dict[str, Any]]
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.key_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "musical_key": self.musical_key,
                "key_confidence": self.key_confidence,
                "mode": self.mode,
                "key_changes_count": len(self.key_changes)
            }
        )


@dataclass
class AudioSentimentAnalysisEvent(BaseEvent):
    """
    Event triggered when sentiment analysis is completed.
    
    Analyzes emotional sentiment and polarity of audio content.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # positive, negative, neutral
    confidence: float
    emotional_intensity: float
    sentiment_timeline: List[Dict[str, Any]]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.sentiment_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "sentiment_score": self.sentiment_score,
                "sentiment_label": self.sentiment_label,
                "confidence": self.confidence,
                "emotional_intensity": self.emotional_intensity
            }
        )


@dataclass
class AudioEmotionDetectionEvent(BaseEvent):
    """
    Event triggered when emotion detection is completed.
    
    Detects and analyzes emotional characteristics in audio.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    primary_emotion: str
    emotion_confidence: float
    emotion_probabilities: Dict[str, float]
    emotional_arousal: float
    emotional_valence: float
    emotion_timeline: List[Dict[str, Any]]
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.emotion_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "primary_emotion": self.primary_emotion,
                "emotion_confidence": self.emotion_confidence,
                "emotional_arousal": self.emotional_arousal,
                "emotional_valence": self.emotional_valence
            }
        )


@dataclass
class AudioInstrumentRecognitionEvent(BaseEvent):
    """
    Event triggered when instrument recognition is completed.
    
    Identifies musical instruments present in audio content.
    """
    user_id: UUID
    file_id: UUID
    recognition_id: UUID
    filename: str
    instruments_detected: List[Dict[str, Any]]
    primary_instrument: str
    instrument_confidence: float
    instrumental_complexity: float
    temporal_presence: Dict[str, List[Dict[str, Any]]]
    recognition_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.instrument_recognition",
            data={
                "file_id": str(self.file_id),
                "recognition_id": str(self.recognition_id),
                "primary_instrument": self.primary_instrument,
                "instrument_confidence": self.instrument_confidence,
                "instruments_count": len(self.instruments_detected)
            }
        )


@dataclass
class AudioLoudnessAnalysisEvent(BaseEvent):
    """
    Event triggered when loudness analysis is completed.
    
    Analyzes loudness characteristics and dynamic range.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    integrated_loudness: float  # LUFS
    loudness_range: float
    peak_level: float
    dynamic_range: float
    loudness_distribution: Dict[str, Any]
    compliance_standards: Dict[str, bool]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.loudness_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "integrated_loudness": self.integrated_loudness,
                "loudness_range": self.loudness_range,
                "peak_level": self.peak_level,
                "dynamic_range": self.dynamic_range
            }
        )


@dataclass
class AudioSpectralAnalysisEvent(BaseEvent):
    """
    Event triggered when spectral analysis is completed.
    
    Analyzes frequency spectrum and spectral characteristics.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    frequency_spectrum: Dict[str, Any]
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    spectral_flatness: float
    harmonic_content: Dict[str, Any]
    noise_characteristics: Dict[str, Any]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.analysis.spectral_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "spectral_centroid": self.spectral_centroid,
                "spectral_bandwidth": self.spectral_bandwidth,
                "spectral_rolloff": self.spectral_rolloff,
                "spectral_flatness": self.spectral_flatness
            }
        )