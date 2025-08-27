"""
Audio Fingerprinting Events - Industrial Grade Fingerprinting & Copyright Protection
=================================================================================

This module handles all events related to audio fingerprinting, copyright detection,
and content protection for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


class FingerprintingMethod(Enum):
    """Audio fingerprinting methods"""
    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    SPECTRAL_HASH = "spectral_hash"
    MFCC = "mfcc"
    CONSTANT_Q = "constant_q"
    WAVELET = "wavelet"
    HYBRID = "hybrid"


class MatchConfidence(Enum):
    """Confidence levels for audio matches"""
    PERFECT = "perfect"  # 95-100%
    HIGH = "high"        # 85-94%
    MEDIUM = "medium"    # 70-84%
    LOW = "low"          # 50-69%
    UNCERTAIN = "uncertain"  # <50%


class ViolationType(Enum):
    """Types of copyright violations"""
    EXACT_COPY = "exact_copy"
    SUBSTANTIAL_SIMILARITY = "substantial_similarity"
    REMIX_UNAUTHORIZED = "remix_unauthorized"
    SAMPLE_UNAUTHORIZED = "sample_unauthorized"
    COVER_UNAUTHORIZED = "cover_unauthorized"
    DERIVATIVE_WORK = "derivative_work"


@dataclass
class AudioFingerprintingStartedEvent(BaseEvent):
    """
    Event triggered when audio fingerprinting process begins.
    
    Initializes comprehensive audio fingerprinting including multiple
    algorithms and cross-validation techniques.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    filename: str
    fingerprinting_methods: List[FingerprintingMethod]
    priority_level: int
    comparison_databases: List[str]
    real_time_enabled: bool
    batch_processing: bool
    estimated_duration: float
    segment_duration: float  # seconds per segment
    overlap_percentage: float
    quality_level: str
    hardware_acceleration: bool
    parallel_processing: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.started",
            event_category=EventCategory.FINGERPRINTING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "methods_count": len(self.fingerprinting_methods),
                "databases_count": len(self.comparison_databases),
                "real_time_enabled": self.real_time_enabled,
                "estimated_duration": self.estimated_duration
            }
        )


@dataclass
class AudioFingerprintingProgressEvent(BaseEvent):
    """
    Event triggered during fingerprinting progress updates.
    
    Provides real-time feedback about fingerprinting pipeline progress.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    current_method: FingerprintingMethod
    segments_processed: int
    total_segments: int
    progress_percentage: float
    elapsed_time: float
    estimated_remaining: float
    current_database: str
    matches_found: int
    processing_speed: float  # segments per second
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.progress",
            event_category=EventCategory.FINGERPRINTING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "current_method": self.current_method.value,
                "progress_percentage": self.progress_percentage,
                "matches_found": self.matches_found
            }
        )


@dataclass
class AudioFingerprintingCompletedEvent(BaseEvent):
    """
    Event triggered when audio fingerprinting is successfully completed.
    
    Contains comprehensive fingerprinting results and generated signatures.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    fingerprint_signatures: Dict[str, str]  # method -> signature
    fingerprint_vectors: Dict[str, List[float]]
    processing_duration: float
    segments_analyzed: int
    databases_searched: List[str]
    total_comparisons: int
    unique_fingerprint_id: str
    fingerprint_quality_score: float
    collision_probability: float
    storage_size: int  # bytes
    indexing_completed: bool
    searchable: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.completed",
            event_category=EventCategory.FINGERPRINTING,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "unique_fingerprint_id": self.unique_fingerprint_id,
                "methods_used": len(self.fingerprint_signatures),
                "quality_score": self.fingerprint_quality_score,
                "total_comparisons": self.total_comparisons
            }
        )


@dataclass
class AudioFingerprintingFailedEvent(BaseEvent):
    """
    Event triggered when audio fingerprinting fails.
    
    Contains detailed error information and recovery options.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    failed_method: FingerprintingMethod
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    segments_processed: int
    total_segments: int
    processing_duration: float
    retry_count: int
    max_retries: int
    is_retryable: bool
    fallback_methods_available: List[FingerprintingMethod]
    suggested_action: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.failed",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "failed_method": self.failed_method.value,
                "error_code": self.error_code,
                "retry_count": self.retry_count,
                "fallback_available": len(self.fallback_methods_available) > 0
            }
        )


@dataclass
class AudioMatchFoundEvent(BaseEvent):
    """
    Event triggered when a potential audio match is detected.
    
    Contains detailed information about the match and similarity metrics.
    """
    user_id: UUID
    file_id: UUID
    match_id: UUID
    matched_file_id: UUID
    matched_filename: str
    similarity_score: float  # 0.0 to 1.0
    confidence_level: MatchConfidence
    matching_method: FingerprintingMethod
    match_duration: float  # seconds of matching content
    match_offset_original: float  # start time in original
    match_offset_matched: float  # start time in matched file
    matching_segments: List[Tuple[float, float]]  # (start, end) pairs
    cross_validation_results: Dict[str, float]
    metadata_comparison: Dict[str, Any]
    visual_similarity: Optional[float] = None
    manual_review_required: bool = False
    false_positive_probability: float = 0.0
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.match_found",
            event_category=EventCategory.DETECTION,
            priority=EventPriority.CRITICAL if self.similarity_score > 0.9 else EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "match_id": str(self.match_id),
                "matched_file_id": str(self.matched_file_id),
                "similarity_score": self.similarity_score,
                "confidence_level": self.confidence_level.value,
                "matching_method": self.matching_method.value,
                "match_duration": self.match_duration
            }
        )


@dataclass
class AudioCopyrightViolationEvent(BaseEvent):
    """
    Event triggered when a copyright violation is detected.
    
    Contains comprehensive violation analysis and recommended actions.
    """
    user_id: UUID
    file_id: UUID
    violation_id: UUID
    original_file_id: UUID
    violation_type: ViolationType
    severity_level: int  # 1-10
    confidence_score: float
    copyrighted_content_percentage: float
    original_owner_id: UUID
    original_title: str
    original_artist: str
    original_label: Optional[str] = None
    registration_date: Optional[datetime] = None
    copyright_territories: List[str] = field(default_factory=list)
    dmca_eligible: bool = True
    takedown_recommended: bool = True
    legal_action_risk: str  # low, medium, high, critical
    estimated_damages: Optional[float] = None
    evidence_package: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.copyright_violation",
            event_category=EventCategory.LEGAL,
            priority=EventPriority.CRITICAL,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "violation_id": str(self.violation_id),
                "original_file_id": str(self.original_file_id),
                "violation_type": self.violation_type.value,
                "severity_level": self.severity_level,
                "confidence_score": self.confidence_score,
                "copyrighted_percentage": self.copyrighted_content_percentage,
                "dmca_eligible": self.dmca_eligible
            }
        )


@dataclass
class AudioSimilarityAnalysisEvent(BaseEvent):
    """
    Event triggered during advanced similarity analysis.
    
    Provides detailed comparison metrics beyond basic fingerprinting.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    comparison_file_id: UUID
    structural_similarity: float
    harmonic_similarity: float
    rhythmic_similarity: float
    melodic_similarity: float
    timbral_similarity: float
    temporal_similarity: float
    overall_similarity: float
    distinguishing_features: List[str]
    similarity_heatmap: List[List[float]]
    time_aligned_comparison: Dict[str, Any]
    perceptual_hash: str
    robust_hash: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.similarity_analysis",
            event_category=EventCategory.ANALYSIS,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "comparison_file_id": str(self.comparison_file_id),
                "overall_similarity": self.overall_similarity,
                "structural_similarity": self.structural_similarity,
                "features_count": len(self.distinguishing_features)
            }
        )


@dataclass
class AudioFingerprintDatabaseUpdatedEvent(BaseEvent):
    """
    Event triggered when fingerprint database is updated.
    
    Tracks database maintenance and indexing operations.
    """
    database_name: str
    update_type: str  # insert, update, delete, rebuild
    records_affected: int
    total_records: int
    index_size: int  # bytes
    update_duration: float
    database_version: str
    optimization_performed: bool
    vacuum_performed: bool
    statistics_updated: bool
    performance_metrics: Dict[str, float]
    backup_created: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.database_updated",
            event_category=EventCategory.SYSTEM,
            priority=EventPriority.LOW,
            metadata={
                "database_name": self.database_name,
                "update_type": self.update_type,
                "records_affected": self.records_affected,
                "total_records": self.total_records,
                "update_duration": self.update_duration,
                "optimization_performed": self.optimization_performed
            }
        )


@dataclass
class AudioFingerprintSearchEvent(BaseEvent):
    """
    Event triggered during fingerprint search operations.
    
    Tracks search performance and results.
    """
    user_id: Optional[UUID]
    search_id: UUID
    query_fingerprint: str
    search_databases: List[str]
    search_duration: float
    results_found: int
    search_method: FingerprintingMethod
    similarity_threshold: float
    max_results: int
    search_filters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    cache_hit: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.search",
            event_category=EventCategory.SEARCH,
            priority=EventPriority.LOW,
            user_id=self.user_id,
            metadata={
                "search_id": str(self.search_id),
                "search_duration": self.search_duration,
                "results_found": self.results_found,
                "search_method": self.search_method.value,
                "cache_hit": self.cache_hit
            }
        )
