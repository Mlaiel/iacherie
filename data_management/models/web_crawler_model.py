"""🕷️ Web Crawler Models - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/models/web_crawler_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Web Crawler Data Models - Production-Ready
Responsibility: Web surveillance and content protection data models
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Web Surveillance → Violation Detection → Automated Takedown → Revenue Recovery

WEB CRAWLER MODEL ARCHITECTURE:
Crawl Scheduling → Multi-Platform Monitoring → Content Fingerprinting → 
Violation Detection → Evidence Collection → Alert Generation → Takedown Processing
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

class CrawlStatus(Enum):
    """
Crawl job status enumeration"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class PlatformType(Enum):
    """Supported platforms for crawling"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    BANDCAMP = "bandcamp"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    GENERIC_WEB = "generic_web"

class ViolationType(Enum):
    """Types of content violations"""

    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    TRADEMARK_VIOLATION = "trademark_violation"
    PLAGIARISM = "plagiarism"
    IMPERSONATION = "impersonation"
    REVENUE_THEFT = "revenue_theft"
    DMCA_VIOLATION = "dmca_violation"
    FAIR_USE_ABUSE = "fair_use_abuse"

class EvidenceType(Enum):
    """Types of evidence collected"""

    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    AUDIO_SAMPLE = "audio_sample"
    HTML_SOURCE = "html_source"
    METADATA = "metadata"
    NETWORK_TRACE = "network_trace"
    API_RESPONSE = "api_response"
    FINGERPRINT_MATCH = "fingerprint_match"

class TakedownStatus(Enum):
    """Takedown request status"""

    PENDING = "pending"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONTENT_REMOVED = "content_removed"
    APPEAL_PENDING = "appeal_pending"
    ESCALATED = "escalated"

@dataclass
class CrawlJobModel:
    """Main crawl job model for web surveillance"""
    job_id: str = field(default_factory=lambda: f"crawl_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    
    # Crawl configuration
    platform: PlatformType = PlatformType.GENERIC_WEB
    search_terms: List[str] = field(default_factory=list)
    target_urls: List[str] = field(default_factory=list)
    fingerprints: List[str] = field(default_factory=list)
    
    # Scheduling
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    
    # Status and priority
    status: CrawlStatus = CrawlStatus.PENDING
    priority: int = 5  # 1-10, 10 being highest
    
    # Crawl parameters
    max_pages: int = 100
    crawl_depth: int = 2
    respect_robots: bool = True
    delay_seconds: float = 1.0
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # Browser configuration
    user_agent: str = "Mozilla/5.0 (compatible; ContentProtectionBot/1.0)"
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy_config: Optional[Dict[str, Any]] = None
    
    # Filtering and processing
    content_filters: Dict[str, Any] = field(default_factory=dict)
    similarity_threshold: float = 0.8
    confidence_threshold: float = 0.7
    
    # Recurrence configuration
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"
    recurrence_interval: int = 1
    
    # Results tracking
    pages_crawled: int = 0
    violations_detected: int = 0
    evidence_collected: int = 0
    last_error: Optional[str] = None
    
    # Metadata and configuration
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Audit fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not self.search_terms and not self.target_urls:
            raise ValueError("Either search_terms or target_urls must be provided")
        
        if self.priority < 1:
            self.priority = 1
        elif self.priority > 10:
            self.priority = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'job_id': self.job_id,
            'creator_id': self.creator_id,
            'platform': self.platform.value,
            'search_terms': self.search_terms,
            'target_urls': self.target_urls,
            'fingerprints': self.fingerprints,
            'scheduled_at': self.scheduled_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'status': self.status.value,
            'priority': self.priority,
            'max_pages': self.max_pages,
            'crawl_depth': self.crawl_depth,
            'respect_robots': self.respect_robots,
            'delay_seconds': self.delay_seconds,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'user_agent': self.user_agent,
            'headers': self.headers,
            'cookies': self.cookies,
            'proxy_config': self.proxy_config,
            'content_filters': self.content_filters,
            'similarity_threshold': self.similarity_threshold,
            'confidence_threshold': self.confidence_threshold,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_interval': self.recurrence_interval,
            'pages_crawled': self.pages_crawled,
            'violations_detected': self.violations_detected,
            'evidence_collected': self.evidence_collected,
            'last_error': self.last_error,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlJobModel':
        """
Create instance from dictionary"""
        # Convert datetime strings
        datetime_fields = ['scheduled_at', 'started_at', 'completed_at', 'next_run_at', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name] and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name].replace('Z', '+00:00'))
        
        # Convert enums
        if 'platform' in data and isinstance(data['platform'], str):
            data['platform'] = PlatformType(data['platform'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = CrawlStatus(data['status'])
        
        return cls(**data)
    
    def is_ready_to_run(self) -> bool:
        """
Check if job is ready to run"""
        return (self.status == CrawlStatus.PENDING and 
                self.scheduled_at <= datetime.now(timezone.utc))
    
    def can_retry(self) -> bool:
        """
Check if job can be retried"""
        return self.status == CrawlStatus.FAILED
    
    def calculate_next_run(self):
        """
Calculate next run time for recurring jobs"""
        if not self.is_recurring or not self.recurrence_pattern:
            return
        
        base_time = self.completed_at or datetime.now(timezone.utc)
        
        if self.recurrence_pattern == "daily":
            self.next_run_at = base_time + timedelta(days=self.recurrence_interval)
        elif self.recurrence_pattern == "weekly":
            self.next_run_at = base_time + timedelta(weeks=self.recurrence_interval)
        elif self.recurrence_pattern == "monthly":
            # Approximate monthly interval
            self.next_run_at = base_time + timedelta(days=30 * self.recurrence_interval)

@dataclass
class DetectedContentModel:
    """Model for content detected during crawling"""
    detection_id: str = field(default_factory=lambda: f"detect_{uuid.uuid4().hex[:12]}")
    job_id: str = ""
    creator_id: str = ""
    original_content_id: str = ""
    
    # Detection details
    detected_url: str = ""
    platform: PlatformType = PlatformType.GENERIC_WEB
    violation_type: ViolationType = ViolationType.COPYRIGHT_INFRINGEMENT
    
    # Similarity metrics
    similarity_score: float = 0.0
    confidence_level: float = 0.0
    fingerprint_matches: List[str] = field(default_factory=list)
    
    # Timing
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Content metadata
    title: Optional[str] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    upload_date: Optional[datetime] = None
    
    # Engagement metrics
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    
    # Revenue impact
    revenue_estimate: Optional[float] = None
    revenue_lost: Optional[float] = None
    
    # Takedown tracking
    takedown_status: TakedownStatus = TakedownStatus.PENDING
    takedown_submitted_at: Optional[datetime] = None
    takedown_completed_at: Optional[datetime] = None
    takedown_reference: Optional[str] = None
    
    # Evidence tracking
    evidence_ids: List[str] = field(default_factory=list)
    
    # Content analysis
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    technical_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Verification and quality
    is_verified: bool = False
    is_false_positive: bool = False
    verification_notes: Optional[str] = None
    
    # Priority and urgency
    urgency_level: int = 5  # 1-10, 10 being most urgent
    
    # Audit fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.similarity_score < 0 or self.similarity_score > 1:
            raise ValueError("Similarity score must be between 0 and 1")
        
        if self.confidence_level < 0 or self.confidence_level > 1:
            raise ValueError("Confidence level must be between 0 and 1")
        
        if self.urgency_level < 1:
            self.urgency_level = 1
        elif self.urgency_level > 10:
            self.urgency_level = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'detection_id': self.detection_id,
            'job_id': self.job_id,
            'creator_id': self.creator_id,
            'original_content_id': self.original_content_id,
            'detected_url': self.detected_url,
            'platform': self.platform.value,
            'violation_type': self.violation_type.value,
            'similarity_score': self.similarity_score,
            'confidence_level': self.confidence_level,
            'fingerprint_matches': self.fingerprint_matches,
            'detected_at': self.detected_at.isoformat(),
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'uploader_id': self.uploader_id,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'share_count': self.share_count,
            'revenue_estimate': self.revenue_estimate,
            'revenue_lost': self.revenue_lost,
            'takedown_status': self.takedown_status.value,
            'takedown_submitted_at': self.takedown_submitted_at.isoformat() if self.takedown_submitted_at else None,
            'takedown_completed_at': self.takedown_completed_at.isoformat() if self.takedown_completed_at else None,
            'takedown_reference': self.takedown_reference,
            'evidence_ids': self.evidence_ids,
            'content_metadata': self.content_metadata,
            'technical_analysis': self.technical_analysis,
            'is_verified': self.is_verified,
            'is_false_positive': self.is_false_positive,
            'verification_notes': self.verification_notes,
            'urgency_level': self.urgency_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectedContentModel':
        """
Create instance from dictionary"""
        # Convert datetime strings
        datetime_fields = ['detected_at', 'upload_date', 'takedown_submitted_at', 
                          'takedown_completed_at', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name] and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name].replace('Z', '+00:00'))
        
        # Convert enums
        if 'platform' in data and isinstance(data['platform'], str):
            data['platform'] = PlatformType(data['platform'])
        if 'violation_type' in data and isinstance(data['violation_type'], str):
            data['violation_type'] = ViolationType(data['violation_type'])
        if 'takedown_status' in data and isinstance(data['takedown_status'], str):
            data['takedown_status'] = TakedownStatus(data['takedown_status'])
        
        return cls(**data)
    
    def is_high_priority(self) -> bool:
        """
Check if detection is high priority"""
        return (self.urgency_level >= 8 or 
                self.similarity_score >= 0.95 or
                (self.revenue_estimate and self.revenue_estimate > 1000))
    
    def requires_immediate_action(self) -> bool:
        """
Check if detection requires immediate action"""
        return (self.urgency_level >= 9 or
                self.violation_type in [ViolationType.COPYRIGHT_INFRINGEMENT, ViolationType.REVENUE_THEFT])

@dataclass
class EvidenceModel:
    """
Model for evidence collected during crawling"""
    evidence_id: str = field(default_factory=lambda: f"evidence_{uuid.uuid4().hex[:12]}")
    detection_id: str = ""
    job_id: str = ""
    
    # Evidence details
    evidence_type: EvidenceType = EvidenceType.SCREENSHOT
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    file_hash: str = ""
    mime_type: str = ""
    
    # Capture details
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    capture_method: str = ""
    capture_url: str = ""
    
    # Quality and verification
    is_verified: bool = False
    legal_weight: float = 1.0  # 0.0 to 1.0, legal significance
    quality_score: float = 1.0  # 0.0 to 1.0, evidence quality
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Storage and access
    storage_location: str = ""
    access_url: Optional[str] = None
    expiry_date: Optional[datetime] = None
    
    # Chain of custody
    collected_by: str = ""
    verified_by: Optional[str] = None
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    
    # Audit fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.legal_weight < 0 or self.legal_weight > 1:
            raise ValueError("Legal weight must be between 0 and 1")
        
        if self.quality_score < 0 or self.quality_score > 1:
            raise ValueError("Quality score must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'evidence_id': self.evidence_id,
            'detection_id': self.detection_id,
            'job_id': self.job_id,
            'evidence_type': self.evidence_type.value,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'mime_type': self.mime_type,
            'captured_at': self.captured_at.isoformat(),
            'capture_method': self.capture_method,
            'capture_url': self.capture_url,
            'is_verified': self.is_verified,
            'legal_weight': self.legal_weight,
            'quality_score': self.quality_score,
            'metadata': self.metadata,
            'technical_metadata': self.technical_metadata,
            'storage_location': self.storage_location,
            'access_url': self.access_url,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'collected_by': self.collected_by,
            'verified_by': self.verified_by,
            'chain_of_custody': self.chain_of_custody,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceModel':
        """
Create instance from dictionary"""
        # Convert datetime strings
        datetime_fields = ['captured_at', 'expiry_date', 'created_at', 'updated_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name] and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name].replace('Z', '+00:00'))
        
        # Convert enums
        if 'evidence_type' in data and isinstance(data['evidence_type'], str):
            data['evidence_type'] = EvidenceType(data['evidence_type'])
        
        return cls(**data)
    
    def is_expired(self) -> bool:
        """
Check if evidence has expired"""
        if not self.expiry_date:
            return False
        return datetime.now(timezone.utc) > self.expiry_date
    
    def add_chain_of_custody_entry(self, action: str, performed_by: str, notes: str = ""):
        """Add entry to chain of custody"""
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'performed_by': performed_by,
            'notes': notes
        }
        self.chain_of_custody.append(entry)

@dataclass
class CrawlMetricsModel:
    """
Model for crawl performance metrics"""
    metrics_id: str = field(default_factory=lambda: f"metrics_{uuid.uuid4().hex[:12]}")
    job_id: str = ""
    
    # Performance metrics
    crawl_duration: float = 0.0  # seconds
    pages_crawled: int = 0
    pages_failed: int = 0
    content_detected: int = 0
    violations_found: int = 0
    evidence_collected: int = 0
    
    # Technical metrics
    average_response_time: float = 0.0  # milliseconds
    bandwidth_used: int = 0  # bytes
    memory_usage: float = 0.0  # MB
    cpu_usage: float = 0.0  # percentage
    
    # Error tracking
    errors_encountered: List[str] = field(default_factory=list)
    warnings_generated: List[str] = field(default_factory=list)
    retry_count: int = 0
    
    # Rate limiting and throttling
    requests_sent: int = 0
    requests_throttled: int = 0
    requests_blocked: int = 0
    
    # Success rates
    success_rate: float = 0.0  # percentage
    detection_accuracy: float = 0.0  # percentage
    false_positive_rate: float = 0.0  # percentage
    
    # Timestamps
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization calculations"""
        # Calculate success rate
        total_requests = self.pages_crawled + self.pages_failed
        if total_requests > 0:
            self.success_rate = (self.pages_crawled / total_requests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for serialization"""
        return {
            'metrics_id': self.metrics_id,
            'job_id': self.job_id,
            'crawl_duration': self.crawl_duration,
            'pages_crawled': self.pages_crawled,
            'pages_failed': self.pages_failed,
            'content_detected': self.content_detected,
            'violations_found': self.violations_found,
            'evidence_collected': self.evidence_collected,
            'average_response_time': self.average_response_time,
            'bandwidth_used': self.bandwidth_used,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'errors_encountered': self.errors_encountered,
            'warnings_generated': self.warnings_generated,
            'retry_count': self.retry_count,
            'requests_sent': self.requests_sent,
            'requests_throttled': self.requests_throttled,
            'requests_blocked': self.requests_blocked,
            'success_rate': self.success_rate,
            'detection_accuracy': self.detection_accuracy,
            'false_positive_rate': self.false_positive_rate,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# Export all models
__all__ = [
    'CrawlJobModel',
    'DetectedContentModel',
    'EvidenceModel',
    'CrawlMetricsModel',
    'CrawlStatus',
    'PlatformType',
    'ViolationType',
    'EvidenceType',
    'TakedownStatus'
]
