"""Audio Fingerprinting Events - Industrial Grade Fingerprinting Event Management
==============================================================================

This module handles all events related to audio fingerprinting, content identification,
and copyright matching for the IA Influencer Agent platform.

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


class FingerprintingMethod(Enum):
    """Audio fingerprinting methods"""
    ACOUSTIC = "acoustic"
    CHROMAPRINT = "chromaprint"
    SHAZAM = "shazam"
    ECHOPRINT = "echoprint"
    NEURAL_HASH = "neural_hash"


class MatchConfidence(Enum):
    """Match confidence levels"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class ViolationType(Enum):
    """Copyright violation types"""
    EXACT_COPY = "exact_copy"
    PARTIAL_COPY = "partial_copy"
    REMIX = "remix"
    COVER = "cover"
    SAMPLE = "sample"


@dataclass
class AudioFingerprintingStartedEvent(BaseEvent):
    """
    Event triggered when audio fingerprinting process begins.
    
    Initializes content identification and copyright matching workflows.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    filename: str
    fingerprinting_method: str
    fingerprinting_profile: str
    reference_databases: List[str]
    estimated_duration: float
    fingerprinting_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.started",
            data={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "fingerprinting_method": self.fingerprinting_method,
                "databases_count": len(self.reference_databases),
                "estimated_duration": self.estimated_duration
            }
        )


@dataclass
class AudioFingerprintingProgressEvent(BaseEvent):
    """
    Event triggered during fingerprinting progress updates.
    
    Provides real-time progress for fingerprinting operations.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    current_stage: str
    progress_percentage: float
    databases_processed: int
    total_databases: int
    matches_found: int
    estimated_time_remaining: float
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.progress",
            data={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "progress_percentage": self.progress_percentage,
                "matches_found": self.matches_found,
                "databases_processed": self.databases_processed
            }
        )


@dataclass
class AudioFingerprintingCompletedEvent(BaseEvent):
    """
    Event triggered when fingerprinting process completes.
    
    Contains comprehensive fingerprinting results and matches.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    filename: str
    fingerprint_hash: str
    total_matches: int
    processing_duration: float
    databases_searched: List[str]
    fingerprint_quality: float
    fingerprinting_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.completed",
            data={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "fingerprint_hash": self.fingerprint_hash,
                "total_matches": self.total_matches,
                "processing_duration": self.processing_duration,
                "fingerprint_quality": self.fingerprint_quality
            }
        )


@dataclass
class AudioFingerprintingFailedEvent(BaseEvent):
    """
    Event triggered when fingerprinting process fails.
    
    Contains error information for debugging and recovery.
    """
    user_id: UUID
    file_id: UUID
    fingerprinting_id: UUID
    filename: str
    error_code: str
    error_message: str
    failure_stage: str
    processing_duration: float
    partial_results: Dict[str, Any] = field(default_factory=dict)
    retry_suggested: bool = True
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.failed",
            data={
                "file_id": str(self.file_id),
                "fingerprinting_id": str(self.fingerprinting_id),
                "error_code": self.error_code,
                "failure_stage": self.failure_stage,
                "retry_suggested": self.retry_suggested
            }
        )


@dataclass
class AudioMatchFoundEvent(BaseEvent):
    """
    Event triggered when a match is found during fingerprinting.
    
    Contains detailed match information and similarity metrics.
    """
    user_id: UUID
    file_id: UUID
    match_id: UUID
    matched_file_id: UUID
    filename: str
    matched_filename: str
    similarity_score: float
    match_confidence: str
    match_duration: float
    match_offset: float
    fingerprinting_method: str
    match_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.match_found",
            data={
                "file_id": str(self.file_id),
                "match_id": str(self.match_id),
                "matched_file_id": str(self.matched_file_id),
                "similarity_score": self.similarity_score,
                "match_confidence": self.match_confidence,
                "match_duration": self.match_duration
            }
        )


@dataclass
class AudioCopyrightViolationEvent(BaseEvent):
    """
    Event triggered when potential copyright violation is detected.
    
    Handles copyright violation detection and enforcement workflows.
    """
    user_id: UUID
    file_id: UUID
    violation_id: UUID
    filename: str
    violation_type: str
    rights_holder_id: UUID
    confidence_score: float
    evidence_data: Dict[str, Any]
    violation_severity: str
    automated_action: str
    notification_required: bool = True
    violation_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.copyright_violation",
            data={
                "file_id": str(self.file_id),
                "violation_id": str(self.violation_id),
                "violation_type": self.violation_type,
                "confidence_score": self.confidence_score,
                "violation_severity": self.violation_severity,
                "automated_action": self.automated_action
            }
        )


@dataclass
class AudioDigitalFingerprintEvent(BaseEvent):
    """
    Event triggered when digital fingerprint is generated or updated.
    
    Manages digital fingerprint creation and maintenance.
    """
    user_id: UUID
    file_id: UUID
    fingerprint_id: UUID
    filename: str
    fingerprint_type: str
    fingerprint_data: str
    fingerprint_algorithm: str
    fingerprint_version: str
    quality_metrics: Dict[str, Any]
    generation_timestamp: datetime
    fingerprint_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.digital_fingerprint",
            data={
                "file_id": str(self.file_id),
                "fingerprint_id": str(self.fingerprint_id),
                "fingerprint_type": self.fingerprint_type,
                "fingerprint_algorithm": self.fingerprint_algorithm,
                "fingerprint_version": self.fingerprint_version
            }
        )


@dataclass
class AudioContentIDEvent(BaseEvent):
    """
    Event triggered for Content ID system operations.
    
    Manages content identification for copyright protection.
    """
    user_id: UUID
    file_id: UUID
    content_id: str
    filename: str
    id_status: str  # registered, matched, disputed, verified
    reference_files: List[str]
    monitoring_enabled: bool
    protection_level: str
    monetization_enabled: bool
    content_id_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.content_id",
            data={
                "file_id": str(self.file_id),
                "content_id": self.content_id,
                "id_status": self.id_status,
                "monitoring_enabled": self.monitoring_enabled,
                "protection_level": self.protection_level,
                "reference_files_count": len(self.reference_files)
            }
        )


@dataclass
class AudioSimilarityAnalysisEvent(BaseEvent):
    """
    Event triggered when similarity analysis is performed.
    
    Analyzes acoustic similarity between audio files.
    """
    user_id: UUID
    file_id: UUID
    analysis_id: UUID
    filename: str
    comparison_file_id: UUID
    similarity_score: float
    analysis_method: str
    feature_comparison: Dict[str, Any]
    temporal_alignment: Dict[str, Any]
    spectral_similarity: Dict[str, Any]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.similarity_analysis",
            data={
                "file_id": str(self.file_id),
                "analysis_id": str(self.analysis_id),
                "comparison_file_id": str(self.comparison_file_id),
                "similarity_score": self.similarity_score,
                "analysis_method": self.analysis_method
            }
        )


@dataclass
class AudioDuplicateDetectionEvent(BaseEvent):
    """
    Event triggered when duplicate content is detected.
    
    Identifies and manages duplicate audio content.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    duplicate_file_ids: List[UUID]
    detection_method: str
    similarity_threshold: float
    exact_duplicates: List[UUID]
    near_duplicates: List[UUID]
    action_taken: str
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.fingerprinting.duplicate_detection",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "duplicates_count": len(self.duplicate_file_ids),
                "exact_duplicates_count": len(self.exact_duplicates),
                "near_duplicates_count": len(self.near_duplicates),
                "action_taken": self.action_taken
            }
        )