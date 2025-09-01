"""Cross-Platform Monitoring Database Model

Enterprise-grade SQLAlchemy model for real-time cross-platform content monitoring,
violation detection, and automated response systems across multiple content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class MonitoringPlatform(Enum):
    """
Monitored content platforms"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    TIDAL = "tidal"
    DEEZER = "deezer"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"


class MonitoringStatus(Enum):
    """Monitoring job status"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


class DetectionMethod(Enum):
    """Content detection methods"""

    FINGERPRINT_MATCHING = "fingerprint_matching"
    VISUAL_RECOGNITION = "visual_recognition"
    AUDIO_ANALYSIS = "audio_analysis"
    TEXT_SIMILARITY = "text_similarity"
    METADATA_COMPARISON = "metadata_comparison"
    REVERSE_IMAGE_SEARCH = "reverse_image_search"
    WATERMARK_DETECTION = "watermark_detection"
    AI_DEEPFAKE_DETECTION = "ai_deepfake_detection"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"


class ResponseAction(Enum):
    """Automated response actions"""

    NOTIFY_OWNER = "notify_owner"
    SEND_TAKEDOWN_REQUEST = "send_takedown_request"
    FILE_DMCA_COMPLAINT = "file_dmca_complaint"
    INITIATE_LEGAL_ACTION = "initiate_legal_action"
    BLOCK_MONETIZATION = "block_monetization"
    CLAIM_REVENUE = "claim_revenue"
    REQUEST_ATTRIBUTION = "request_attribution"
    NEGOTIATE_LICENSE = "negotiate_license"
    ESCALATE_TO_HUMAN = "escalate_to_human"


class PlatformMonitoring(Base):
    """
    Cross-Platform Monitoring Configuration Model
    
    Manages real-time monitoring configurations for content protection across
    multiple platforms with automated detection and response systems.
    """
    __tablename__ = "platform_monitoring"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Platform configuration
    platform = Column(SQLEnum(MonitoringPlatform), nullable=False, index=True)
    monitoring_status = Column(SQLEnum(MonitoringStatus), default=MonitoringStatus.ACTIVE, index=True)
    api_credentials_id = Column(UUID(as_uuid=True), nullable=True)  # Encrypted credentials reference
    
    # Detection settings
    detection_methods = Column(ARRAY(SQLEnum(DetectionMethod)), nullable=False)
    similarity_threshold = Column(Float, default=0.85)
    scan_frequency_minutes = Column(Integer, default=60)
    deep_scan_enabled = Column(Boolean, default=True)
    
    # Automated response configuration
    automated_responses = Column(ARRAY(SQLEnum(ResponseAction)), nullable=True)
    response_delay_minutes = Column(Integer, default=5)  # Delay before automated action
    escalation_threshold = Column(Float, default=0.95)  # When to escalate to human
    
    # Search parameters
    search_keywords = Column(ARRAY(String), nullable=True)
    search_hashtags = Column(ARRAY(String), nullable=True)
    search_usernames = Column(ARRAY(String), nullable=True)
    exclude_channels = Column(ARRAY(String), nullable=True)  # Channels to ignore
    
    # Geographic and temporal filters
    target_regions = Column(ARRAY(String), nullable=True)  # Country codes
    exclude_regions = Column(ARRAY(String), nullable=True)
    monitoring_hours_utc = Column(JSON, nullable=True)  # Active monitoring hours
    timezone = Column(String(50), default="UTC")
    
    # Performance metrics
    total_scans_performed = Column(Integer, default=0)
    matches_found = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    successful_takedowns = Column(Integer, default=0)
    
    # Rate limiting and quotas
    daily_scan_limit = Column(Integer, default=10000)
    current_daily_usage = Column(Integer, default=0)
    rate_limit_reset_time = Column(DateTime(timezone=True), nullable=True)
    quota_exceeded_count = Column(Integer, default=0)
    
    # Error tracking
    last_error_message = Column(Text, nullable=True)
    consecutive_errors = Column(Integer, default=0)
    last_successful_scan = Column(DateTime(timezone=True), nullable=True)
    
    # Advanced features
    ai_enhancement_enabled = Column(Boolean, default=True)
    learning_mode_enabled = Column(Boolean, default=True)
    priority_level = Column(Integer, default=5)  # 1-10 priority scale
    
    # Financial tracking
    monitoring_cost_daily = Column(Numeric(10, 4), default=Decimal('0.0'))
    api_usage_cost = Column(Numeric(10, 4), default=Decimal('0.0'))
    total_cost_to_date = Column(Numeric(18, 8), default=Decimal('0.0'))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    next_scan_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_premium_monitoring = Column(Boolean, default=False)
    requires_human_review = Column(Boolean, default=False)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="platform_monitoring")
    scan_results = relationship("ScanResult", back_populates="platform_monitoring", cascade="all, delete-orphan")
    violation_detections = relationship("ViolationDetection", back_populates="platform_monitoring", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_platform_monitoring_user_platform', 'user_id', 'platform'),
        Index('idx_platform_monitoring_status_scan', 'monitoring_status', 'next_scan_at'),
        Index('idx_platform_monitoring_priority', 'priority_level', 'is_active'),
        Index('idx_platform_monitoring_performance', 'total_scans_performed', 'matches_found'),
        Index('idx_platform_monitoring_cost', 'monitoring_cost_daily', 'total_cost_to_date'),
    )
    
    def __repr__(self):
        return f"<PlatformMonitoring(id={self.id}, platform={self.platform.value}, status={self.monitoring_status.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "content_fingerprint_id": str(self.content_fingerprint_id),
            "user_id": str(self.user_id),
            "platform": self.platform.value,
            "monitoring_status": self.monitoring_status.value,
            "detection_methods": [method.value for method in self.detection_methods] if self.detection_methods else [],
            "similarity_threshold": self.similarity_threshold,
            "scan_frequency_minutes": self.scan_frequency_minutes,
            "deep_scan_enabled": self.deep_scan_enabled,
            "automated_responses": [action.value for action in self.automated_responses] if self.automated_responses else [],
            "response_delay_minutes": self.response_delay_minutes,
            "escalation_threshold": self.escalation_threshold,
            "search_keywords": self.search_keywords,
            "search_hashtags": self.search_hashtags,
            "search_usernames": self.search_usernames,
            "exclude_channels": self.exclude_channels,
            "target_regions": self.target_regions,
            "exclude_regions": self.exclude_regions,
            "monitoring_hours_utc": self.monitoring_hours_utc,
            "timezone": self.timezone,
            "total_scans_performed": self.total_scans_performed,
            "matches_found": self.matches_found,
            "false_positives": self.false_positives,
            "successful_takedowns": self.successful_takedowns,
            "daily_scan_limit": self.daily_scan_limit,
            "current_daily_usage": self.current_daily_usage,
            "rate_limit_reset_time": self.rate_limit_reset_time.isoformat() if self.rate_limit_reset_time else None,
            "quota_exceeded_count": self.quota_exceeded_count,
            "last_error_message": self.last_error_message,
            "consecutive_errors": self.consecutive_errors,
            "last_successful_scan": self.last_successful_scan.isoformat() if self.last_successful_scan else None,
            "ai_enhancement_enabled": self.ai_enhancement_enabled,
            "learning_mode_enabled": self.learning_mode_enabled,
            "priority_level": self.priority_level,
            "monitoring_cost_daily": float(self.monitoring_cost_daily) if self.monitoring_cost_daily else None,
            "api_usage_cost": float(self.api_usage_cost) if self.api_usage_cost else None,
            "total_cost_to_date": float(self.total_cost_to_date) if self.total_cost_to_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "next_scan_at": self.next_scan_at.isoformat() if self.next_scan_at else None,
            "is_active": self.is_active,
            "is_premium_monitoring": self.is_premium_monitoring,
            "requires_human_review": self.requires_human_review
        }


class ScanResult(Base):
    """
    Platform Scan Result Model
    
    Stores detailed results from platform scans including matches and potential violations.
    """
    __tablename__ = "scan_results"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_monitoring_id = Column(UUID(as_uuid=True), ForeignKey('platform_monitoring.id'), nullable=False, index=True)
    
    # Scan details
    scan_started_at = Column(DateTime(timezone=True), nullable=False)
    scan_completed_at = Column(DateTime(timezone=True), nullable=False)
    scan_duration_seconds = Column(Integer, nullable=False)
    
    # Results summary
    total_items_scanned = Column(Integer, default=0)
    potential_matches_found = Column(Integer, default=0)
    high_confidence_matches = Column(Integer, default=0)
    false_positives_filtered = Column(Integer, default=0)
    
    # Performance metrics
    scan_success_rate = Column(Float, default=100.0)
    api_response_time_avg = Column(Float, nullable=True)
    bandwidth_used_mb = Column(Float, default=0.0)
    
    # Detailed results
    scan_results_data = Column(JSON, nullable=True)  # Detailed scan data
    match_details = Column(JSON, nullable=True)  # Specific match information
    errors_encountered = Column(JSON, nullable=True)  # Any errors during scan
    
    # Status and flags
    scan_completed_successfully = Column(Boolean, default=True)
    requires_manual_review = Column(Boolean, default=False)
    has_high_priority_matches = Column(Boolean, default=False)
    
    # Relationships
    platform_monitoring = relationship("PlatformMonitoring", back_populates="scan_results")
    
    def __repr__(self):
        return f"<ScanResult(id={self.id}, matches={self.potential_matches_found}, duration={self.scan_duration_seconds}s)>"


class ViolationDetection(Base):
    """
    Violation Detection Model
    
    Records specific content violations detected during platform monitoring.
    """
    __tablename__ = "violation_detections"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_monitoring_id = Column(UUID(as_uuid=True), ForeignKey('platform_monitoring.id'), nullable=False, index=True)
    scan_result_id = Column(UUID(as_uuid=True), ForeignKey('scan_results.id'), nullable=True, index=True)
    
    # Violation details
    detected_url = Column(Text, nullable=False)
    violating_content_title = Column(String(500), nullable=True)
    violating_user_id = Column(String(255), nullable=True)
    violating_username = Column(String(255), nullable=True)
    
    # Detection metrics
    similarity_score = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    detection_method_used = Column(SQLEnum(DetectionMethod), nullable=False)
    
    # Content analysis
    content_duration_seconds = Column(Integer, nullable=True)
    upload_date = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    engagement_metrics = Column(JSON, nullable=True)
    
    # Evidence collection
    screenshot_url = Column(Text, nullable=True)
    audio_sample_url = Column(Text, nullable=True)
    metadata_snapshot = Column(JSON, nullable=True)
    hash_verification = Column(String(255), nullable=True)
    
    # Response tracking
    automated_response_sent = Column(Boolean, default=False)
    response_action_taken = Column(SQLEnum(ResponseAction), nullable=True)
    response_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    violation_status = Column(String(50), default="detected")  # detected, reported, resolved, dismissed
    resolution_method = Column(String(100), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Financial impact
    estimated_revenue_loss = Column(Numeric(18, 8), nullable=True)
    views_at_detection = Column(Integer, default=0)
    projected_damages = Column(Numeric(18, 8), nullable=True)
    
    # Priority and classification
    violation_severity = Column(String(20), default="medium")  # low, medium, high, critical
    requires_immediate_action = Column(Boolean, default=False)
    legal_action_recommended = Column(Boolean, default=False)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    first_seen_at = Column(DateTime(timezone=True), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    platform_monitoring = relationship("PlatformMonitoring", back_populates="violation_detections")
    scan_result = relationship("ScanResult")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_violation_detection_similarity', 'similarity_score', 'confidence_level'),
        Index('idx_violation_detection_status', 'violation_status', 'violation_severity'),
        Index('idx_violation_detection_response', 'automated_response_sent', 'response_action_taken'),
        Index('idx_violation_detection_financial', 'estimated_revenue_loss', 'projected_damages'),
        Index('idx_violation_detection_priority', 'requires_immediate_action', 'legal_action_recommended'),
    )
    
    def __repr__(self):
        return f"<ViolationDetection(id={self.id}, score={self.similarity_score}, status={self.violation_status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "platform_monitoring_id": str(self.platform_monitoring_id),
            "scan_result_id": str(self.scan_result_id) if self.scan_result_id else None,
            "detected_url": self.detected_url,
            "violating_content_title": self.violating_content_title,
            "violating_user_id": self.violating_user_id,
            "violating_username": self.violating_username,
            "similarity_score": self.similarity_score,
            "confidence_level": self.confidence_level,
            "detection_method_used": self.detection_method_used.value,
            "content_duration_seconds": self.content_duration_seconds,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "view_count": self.view_count,
            "engagement_metrics": self.engagement_metrics,
            "screenshot_url": self.screenshot_url,
            "audio_sample_url": self.audio_sample_url,
            "metadata_snapshot": self.metadata_snapshot,
            "hash_verification": self.hash_verification,
            "automated_response_sent": self.automated_response_sent,
            "response_action_taken": self.response_action_taken.value if self.response_action_taken else None,
            "response_sent_at": self.response_sent_at.isoformat() if self.response_sent_at else None,
            "violation_status": self.violation_status,
            "resolution_method": self.resolution_method,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "estimated_revenue_loss": float(self.estimated_revenue_loss) if self.estimated_revenue_loss else None,
            "views_at_detection": self.views_at_detection,
            "projected_damages": float(self.projected_damages) if self.projected_damages else None,
            "violation_severity": self.violation_severity,
            "requires_immediate_action": self.requires_immediate_action,
            "legal_action_recommended": self.legal_action_recommended,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None
        }
