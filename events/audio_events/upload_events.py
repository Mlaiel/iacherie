"""Audio Upload Events - Industrial Grade Upload Event Management
============================================================

This module handles all events related to audio file uploads including validation,
processing, storage, and notification events for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from ...core.events.base_event import BaseEvent, EventPriority, EventCategory


@dataclass
class AudioUploadStartedEvent(BaseEvent):
    """
    Event triggered when an audio upload process begins.
    
    This event contains all necessary information about the upload session
    and is used to initialize tracking and processing pipelines.
    """
    user_id: UUID
    upload_id: UUID
    filename: str
    file_size: int
    file_format: str
    upload_session_id: str
    client_ip: str
    user_agent: str
    expected_duration: Optional[float] = None
    upload_source: str = "web_interface"
    chunk_size: int = 1024 * 1024  # 1MB default
    total_chunks: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.started",
            event_category=EventCategory.UPLOAD,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "filename": self.filename,
                "file_size": self.file_size,
                "file_format": self.file_format,
                "upload_source": self.upload_source,
                **self.metadata
            }
        )


@dataclass  
class AudioUploadProgressEvent(BaseEvent):
    """
    Event triggered during audio upload progress updates.
    
    Provides real-time feedback about upload progress for UI updates
    and monitoring systems.
    """
    user_id: UUID
    upload_id: UUID
    upload_session_id: str
    bytes_uploaded: int
    total_bytes: int
    progress_percentage: float
    upload_speed: float  # bytes per second
    estimated_time_remaining: float  # seconds
    current_chunk: int
    total_chunks: int
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.progress",
            event_category=EventCategory.UPLOAD,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "progress_percentage": self.progress_percentage,
                "upload_speed": self.upload_speed,
                "estimated_time_remaining": self.estimated_time_remaining
            }
        )


@dataclass
class AudioUploadCompletedEvent(BaseEvent):
    """
    Event triggered when an audio upload is successfully completed.
    
    Contains comprehensive information about the uploaded file and
    triggers downstream processing pipelines.
    """
    user_id: UUID
    upload_id: UUID
    file_id: UUID
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_format: str
    duration: float
    sample_rate: int
    bit_rate: int
    channels: int
    upload_duration: float  # seconds taken to upload
    checksum: str
    storage_provider: str
    storage_bucket: str
    storage_key: str
    content_type: str
    upload_session_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.completed",
            event_category=EventCategory.UPLOAD,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "file_id": str(self.file_id),
                "filename": self.filename,
                "file_size": self.file_size,
                "duration": self.duration,
                "sample_rate": self.sample_rate,
                "bit_rate": self.bit_rate,
                "channels": self.channels,
                "checksum": self.checksum,
                **self.metadata
            }
        )


@dataclass
class AudioUploadFailedEvent(BaseEvent):
    """
    Event triggered when an audio upload fails.
    
    Contains detailed error information for debugging and user notification.
    """
    user_id: UUID
    upload_id: UUID
    upload_session_id: str
    filename: str
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
    failure_stage: str  # validation, upload, processing, storage
    bytes_uploaded: int
    total_bytes: int
    retry_count: int
    is_retryable: bool
    suggested_action: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.failed",
            event_category=EventCategory.ERROR,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "error_code": self.error_code,
                "error_message": self.error_message,
                "failure_stage": self.failure_stage,
                "retry_count": self.retry_count,
                "is_retryable": self.is_retryable,
                "suggested_action": self.suggested_action
            }
        )


@dataclass
class AudioUploadValidationEvent(BaseEvent):
    """
    Event triggered during audio file validation process.
    
    Contains validation results and any issues found with the uploaded file.
    """
    user_id: UUID
    upload_id: UUID
    file_id: UUID
    filename: str
    validation_status: str  # passed, failed, warning
    validation_results: Dict[str, Any]
    format_validation: Dict[str, Any]
    content_validation: Dict[str, Any]
    security_validation: Dict[str, Any]
    quality_validation: Dict[str, Any]
    copyright_validation: Dict[str, Any]
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.validation",
            event_category=EventCategory.VALIDATION,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "file_id": str(self.file_id),
                "validation_status": self.validation_status,
                "warnings_count": len(self.warnings),
                "errors_count": len(self.errors),
                "recommendations_count": len(self.recommendations)
            }
        )


@dataclass
class AudioUploadVirusScanEvent(BaseEvent):
    """
    Event triggered during virus/malware scanning of uploaded audio files.
    
    Ensures security compliance before file processing begins.
    """
    user_id: UUID
    upload_id: UUID
    file_id: UUID
    filename: str
    scan_status: str  # clean, infected, suspicious, failed
    scan_engine: str
    scan_version: str
    threats_detected: List[Dict[str, Any]] = field(default_factory=list)
    scan_duration: float
    quarantine_required: bool = False
    scan_details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.virus_scan",
            event_category=EventCategory.SECURITY,
            priority=EventPriority.CRITICAL if self.scan_status == "infected" else EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "file_id": str(self.file_id),
                "scan_status": self.scan_status,
                "scan_engine": self.scan_engine,
                "threats_count": len(self.threats_detected),
                "quarantine_required": self.quarantine_required
            }
        )


@dataclass
class AudioUploadMetadataExtractedEvent(BaseEvent):
    """
    Event triggered when metadata extraction from audio file is completed.
    
    Contains all extracted metadata including ID3 tags, technical properties,
    and embedded information.
    """
    user_id: UUID
    upload_id: UUID
    file_id: UUID
    filename: str
    extracted_metadata: Dict[str, Any]
    id3_tags: Dict[str, Any]
    technical_metadata: Dict[str, Any]
    embedded_artwork: Optional[Dict[str, Any]] = None
    embedded_lyrics: Optional[str] = None
    copyright_info: Optional[Dict[str, Any]] = None
    creation_timestamp: Optional[datetime] = None
    recording_location: Optional[Dict[str, Any]] = None
    equipment_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.metadata_extracted",
            event_category=EventCategory.PROCESSING,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "file_id": str(self.file_id),
                "has_artwork": self.embedded_artwork is not None,
                "has_lyrics": self.embedded_lyrics is not None,
                "has_copyright_info": self.copyright_info is not None,
                "metadata_fields_count": len(self.extracted_metadata)
            }
        )


@dataclass
class AudioUploadDuplicateDetectedEvent(BaseEvent):
    """
    Event triggered when a duplicate audio file is detected during upload.
    
    Prevents unnecessary storage and processing of identical content.
    """
    user_id: UUID
    upload_id: UUID
    filename: str
    duplicate_file_id: UUID
    duplicate_filename: str
    similarity_score: float
    duplicate_detection_method: str  # checksum, fingerprint, metadata
    original_upload_date: datetime
    duplicate_user_id: UUID
    action_taken: str  # reject, merge, allow_duplicate
    user_notified: bool = False
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.duplicate_detected",
            event_category=EventCategory.VALIDATION,
            priority=EventPriority.MEDIUM,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "duplicate_file_id": str(self.duplicate_file_id),
                "similarity_score": self.similarity_score,
                "detection_method": self.duplicate_detection_method,
                "action_taken": self.action_taken
            }
        )


@dataclass
class AudioUploadQuotaExceededEvent(BaseEvent):
    """
    Event triggered when user upload quota is exceeded.
    
    Handles quota enforcement and upgrade suggestions.
    """
    user_id: UUID
    upload_id: UUID
    filename: str
    file_size: int
    current_usage: int
    quota_limit: int
    quota_type: str  # storage, monthly_uploads, file_count
    quota_period: str
    upgrade_required: bool
    suggested_plan: Optional[str] = None
    grace_period_remaining: Optional[int] = None
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.upload.quota_exceeded",
            event_category=EventCategory.BUSINESS,
            priority=EventPriority.HIGH,
            user_id=self.user_id,
            metadata={
                "upload_id": str(self.upload_id),
                "file_size": self.file_size,
                "current_usage": self.current_usage,
                "quota_limit": self.quota_limit,
                "quota_type": self.quota_type,
                "upgrade_required": self.upgrade_required
            }
        )
