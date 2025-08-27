"""
Content Lifecycle Configuration Module
======================================

Manages content lifecycle states, transitions, and business rules for multi-format content.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


class ContentStatus(str, Enum):
    """Content lifecycle status states."""
    DRAFT = "draft"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    VALIDATED = "validated"
    FINGERPRINTED = "fingerprinted"
    PROTECTED = "protected"
    PUBLISHED = "published"
    LIVE = "live"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    QUARANTINED = "quarantined"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    MONETIZED = "monetized"


class ContentEvent(str, Enum):
    """Content lifecycle events that trigger state changes."""
    UPLOAD = "upload"
    VALIDATE = "validate"
    PROCESS = "process"
    FINGERPRINT = "fingerprint"
    PROTECT = "protect"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    SUSPEND = "suspend"
    DELETE = "delete"
    QUARANTINE = "quarantine"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    MONETIZE = "monetize"
    RESTORE = "restore"


class ContentPriority(str, Enum):
    """Content processing priority levels."""
    ULTRA_HIGH = "ultra_high"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class ContentCategory(str, Enum):
    """Content categorization for business logic."""
    MUSIC_ORIGINAL = "music_original"
    MUSIC_COVER = "music_cover"
    MUSIC_REMIX = "music_remix"
    VIDEO_ORIGINAL = "video_original"
    VIDEO_COMPILATION = "video_compilation"
    VIDEO_TUTORIAL = "video_tutorial"
    IMAGE_PHOTOGRAPHY = "image_photography"
    IMAGE_ARTWORK = "image_artwork"
    IMAGE_INFOGRAPHIC = "image_infographic"
    TEXT_BLOG = "text_blog"
    TEXT_SCRIPT = "text_script"
    TEXT_LYRICS = "text_lyrics"
    PODCAST_EPISODE = "podcast_episode"
    LIVESTREAM_PERFORMANCE = "livestream_performance"
    MIXED_MEDIA_PROJECT = "mixed_media_project"


@dataclass
class StateTransition:
    """Defines a valid state transition."""
    from_state: ContentStatus
    to_state: ContentStatus
    event: ContentEvent
    required_permissions: Set[str]
    conditions: Dict[str, Union[str, int, bool]]
    auto_transition: bool = False
    timeout_hours: Optional[int] = None


@dataclass
class ContentMetadata:
    """Content metadata structure."""
    title: str
    description: Optional[str] = None
    tags: List[str] = None
    genre: Optional[str] = None
    language: str = "en"
    explicit_content: bool = False
    copyright_info: Optional[Dict[str, str]] = None
    collaboration_info: Optional[Dict[str, str]] = None


class ContentLifecycleConfig:
    """Enterprise content lifecycle management configuration."""

    # Valid state transitions
    STATE_TRANSITIONS = [
        # Initial upload flow
        StateTransition(
            from_state=ContentStatus.DRAFT,
            to_state=ContentStatus.UPLOADED,
            event=ContentEvent.UPLOAD,
            required_permissions={"content:create"},
            conditions={"file_present": True, "format_supported": True},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.UPLOADED,
            to_state=ContentStatus.PROCESSING,
            event=ContentEvent.PROCESS,
            required_permissions=set(),
            conditions={"validation_passed": True},
            auto_transition=True,
            timeout_hours=1
        ),
        StateTransition(
            from_state=ContentStatus.PROCESSING,
            to_state=ContentStatus.VALIDATED,
            event=ContentEvent.VALIDATE,
            required_permissions=set(),
            conditions={"processing_complete": True, "quality_check_passed": True},
            auto_transition=True,
            timeout_hours=2
        ),
        StateTransition(
            from_state=ContentStatus.VALIDATED,
            to_state=ContentStatus.FINGERPRINTED,
            event=ContentEvent.FINGERPRINT,
            required_permissions=set(),
            conditions={"fingerprint_generated": True, "vector_stored": True},
            auto_transition=True,
            timeout_hours=1
        ),
        StateTransition(
            from_state=ContentStatus.FINGERPRINTED,
            to_state=ContentStatus.PROTECTED,
            event=ContentEvent.PROTECT,
            required_permissions=set(),
            conditions={"protection_rules_applied": True, "license_generated": True},
            auto_transition=True,
            timeout_hours=1
        ),
        StateTransition(
            from_state=ContentStatus.PROTECTED,
            to_state=ContentStatus.PUBLISHED,
            event=ContentEvent.PUBLISH,
            required_permissions={"content:publish"},
            conditions={"metadata_complete": True, "seo_optimized": True},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.PUBLISHED,
            to_state=ContentStatus.LIVE,
            event=ContentEvent.PUBLISH,
            required_permissions=set(),
            conditions={"distribution_complete": True, "monitoring_active": True},
            auto_transition=True,
            timeout_hours=1
        ),
        StateTransition(
            from_state=ContentStatus.LIVE,
            to_state=ContentStatus.MONETIZED,
            event=ContentEvent.MONETIZE,
            required_permissions={"finance:manage_payouts"},
            conditions={"payment_configured": True, "revenue_tracking_enabled": True},
            auto_transition=False
        ),
        
        # Archive flow
        StateTransition(
            from_state=ContentStatus.LIVE,
            to_state=ContentStatus.ARCHIVED,
            event=ContentEvent.ARCHIVE,
            required_permissions={"content:update"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.MONETIZED,
            to_state=ContentStatus.ARCHIVED,
            event=ContentEvent.ARCHIVE,
            required_permissions={"content:update"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.ARCHIVED,
            to_state=ContentStatus.LIVE,
            event=ContentEvent.RESTORE,
            required_permissions={"content:update"},
            conditions={"content_valid": True},
            auto_transition=False
        ),
        
        # Suspension flow
        StateTransition(
            from_state=ContentStatus.LIVE,
            to_state=ContentStatus.SUSPENDED,
            event=ContentEvent.SUSPEND,
            required_permissions={"content:moderate"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.MONETIZED,
            to_state=ContentStatus.SUSPENDED,
            event=ContentEvent.SUSPEND,
            required_permissions={"content:moderate"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.SUSPENDED,
            to_state=ContentStatus.LIVE,
            event=ContentEvent.RESTORE,
            required_permissions={"content:moderate"},
            conditions={"suspension_resolved": True},
            auto_transition=False
        ),
        
        # Review and moderation flow
        StateTransition(
            from_state=ContentStatus.UPLOADED,
            to_state=ContentStatus.PENDING_REVIEW,
            event=ContentEvent.REVIEW,
            required_permissions=set(),
            conditions={"flagged_for_review": True},
            auto_transition=True
        ),
        StateTransition(
            from_state=ContentStatus.PENDING_REVIEW,
            to_state=ContentStatus.PROCESSING,
            event=ContentEvent.APPROVE,
            required_permissions={"content:moderate"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.PENDING_REVIEW,
            to_state=ContentStatus.REJECTED,
            event=ContentEvent.REJECT,
            required_permissions={"content:moderate"},
            conditions={},
            auto_transition=False
        ),
        
        # Quarantine flow
        StateTransition(
            from_state=ContentStatus.UPLOADED,
            to_state=ContentStatus.QUARANTINED,
            event=ContentEvent.QUARANTINE,
            required_permissions=set(),
            conditions={"security_risk_detected": True},
            auto_transition=True
        ),
        StateTransition(
            from_state=ContentStatus.PROCESSING,
            to_state=ContentStatus.QUARANTINED,
            event=ContentEvent.QUARANTINE,
            required_permissions=set(),
            conditions={"malware_detected": True},
            auto_transition=True
        ),
        
        # Deletion flow
        StateTransition(
            from_state=ContentStatus.DRAFT,
            to_state=ContentStatus.DELETED,
            event=ContentEvent.DELETE,
            required_permissions={"content:delete"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.REJECTED,
            to_state=ContentStatus.DELETED,
            event=ContentEvent.DELETE,
            required_permissions={"content:delete"},
            conditions={},
            auto_transition=False
        ),
        StateTransition(
            from_state=ContentStatus.QUARANTINED,
            to_state=ContentStatus.DELETED,
            event=ContentEvent.DELETE,
            required_permissions={"content:delete"},
            conditions={},
            auto_transition=False
        )
    ]

    # Status-specific configurations
    STATUS_CONFIGS = {
        ContentStatus.DRAFT: {
            "max_duration_days": 30,
            "auto_cleanup": True,
            "editable": True,
            "visible": False,
            "backup_required": False
        },
        ContentStatus.UPLOADED: {
            "max_duration_hours": 24,
            "auto_cleanup": False,
            "editable": True,
            "visible": False,
            "backup_required": True,
            "processing_priority": ContentPriority.HIGH
        },
        ContentStatus.PROCESSING: {
            "max_duration_hours": 6,
            "auto_cleanup": False,
            "editable": False,
            "visible": False,
            "backup_required": True,
            "retry_attempts": 3
        },
        ContentStatus.VALIDATED: {
            "max_duration_hours": 2,
            "auto_cleanup": False,
            "editable": False,
            "visible": False,
            "backup_required": True
        },
        ContentStatus.FINGERPRINTED: {
            "max_duration_hours": 2,
            "auto_cleanup": False,
            "editable": False,
            "visible": False,
            "backup_required": True
        },
        ContentStatus.PROTECTED: {
            "max_duration_hours": 24,
            "auto_cleanup": False,
            "editable": True,
            "visible": True,
            "backup_required": True,
            "metadata_required": True
        },
        ContentStatus.PUBLISHED: {
            "max_duration_hours": 2,
            "auto_cleanup": False,
            "editable": False,
            "visible": True,
            "backup_required": True,
            "distribution_required": True
        },
        ContentStatus.LIVE: {
            "max_duration_days": -1,  # Indefinite
            "auto_cleanup": False,
            "editable": False,
            "visible": True,
            "backup_required": True,
            "monitoring_enabled": True,
            "analytics_tracking": True
        },
        ContentStatus.MONETIZED: {
            "max_duration_days": -1,  # Indefinite
            "auto_cleanup": False,
            "editable": False,
            "visible": True,
            "backup_required": True,
            "monitoring_enabled": True,
            "analytics_tracking": True,
            "revenue_tracking": True
        },
        ContentStatus.ARCHIVED: {
            "max_duration_days": 365 * 5,  # 5 years
            "auto_cleanup": True,
            "editable": False,
            "visible": False,
            "backup_required": True,
            "monitoring_enabled": False
        },
        ContentStatus.SUSPENDED: {
            "max_duration_days": 30,
            "auto_cleanup": False,
            "editable": False,
            "visible": False,
            "backup_required": True,
            "review_required": True
        },
        ContentStatus.DELETED: {
            "max_duration_days": 90,  # Soft delete retention
            "auto_cleanup": True,
            "editable": False,
            "visible": False,
            "backup_required": False
        },
        ContentStatus.QUARANTINED: {
            "max_duration_days": 7,
            "auto_cleanup": True,
            "editable": False,
            "visible": False,
            "backup_required": False,
            "security_scan_required": True
        },
        ContentStatus.PENDING_REVIEW: {
            "max_duration_days": 7,
            "auto_cleanup": False,
            "editable": False,
            "visible": False,
            "backup_required": True,
            "review_required": True
        },
        ContentStatus.REJECTED: {
            "max_duration_days": 30,
            "auto_cleanup": True,
            "editable": False,
            "visible": False,
            "backup_required": False
        }
    }

    # Category-specific business rules
    CATEGORY_RULES = {
        ContentCategory.MUSIC_ORIGINAL: {
            "copyright_verification": True,
            "metadata_requirements": ["genre", "album", "artist", "duration"],
            "quality_standards": {"bitrate_min": 320000, "format_preferred": "flac"},
            "protection_level": "high",
            "monetization_eligible": True,
            "collaboration_friendly": True
        },
        ContentCategory.MUSIC_COVER: {
            "copyright_verification": True,
            "original_work_attribution": True,
            "metadata_requirements": ["original_artist", "cover_artist", "genre"],
            "quality_standards": {"bitrate_min": 256000},
            "protection_level": "medium",
            "monetization_eligible": True,
            "royalty_sharing_required": True
        },
        ContentCategory.VIDEO_ORIGINAL: {
            "copyright_verification": True,
            "metadata_requirements": ["duration", "resolution", "fps"],
            "quality_standards": {"resolution_min": "720p", "fps_min": 24},
            "protection_level": "high",
            "monetization_eligible": True,
            "content_id_required": True
        },
        ContentCategory.IMAGE_PHOTOGRAPHY: {
            "copyright_verification": True,
            "metadata_requirements": ["camera_info", "location", "date_taken"],
            "quality_standards": {"resolution_min": "1920x1080", "format_preferred": "png"},
            "protection_level": "high",
            "watermarking_enabled": True,
            "print_licensing_available": True
        },
        ContentCategory.TEXT_BLOG: {
            "plagiarism_check": True,
            "metadata_requirements": ["word_count", "reading_time", "category"],
            "quality_standards": {"readability_score_min": 60},
            "protection_level": "medium",
            "seo_optimization": True,
            "syndication_allowed": True
        },
        ContentCategory.PODCAST_EPISODE: {
            "transcript_generation": True,
            "metadata_requirements": ["episode_number", "series", "duration"],
            "quality_standards": {"bitrate_min": 128000, "format_preferred": "mp3"},
            "protection_level": "medium",
            "sponsorship_opportunities": True,
            "rss_feed_enabled": True
        }
    }

    # Automation rules
    AUTOMATION_RULES = {
        "auto_processing": {
            "enabled": True,
            "batch_size": 10,
            "processing_hours": [0, 6, 12, 18],  # UTC hours
            "priority_queue_enabled": True
        },
        "auto_protection": {
            "enabled": True,
            "fingerprint_threshold": 0.85,
            "similarity_check": True,
            "duplicate_detection": True
        },
        "auto_moderation": {
            "enabled": True,
            "content_scanning": True,
            "explicit_content_detection": True,
            "copyright_infringement_check": True,
            "quarantine_on_violation": True
        },
        "auto_cleanup": {
            "enabled": True,
            "cleanup_hours": [2, 14],  # UTC hours
            "soft_delete_retention_days": 90,
            "permanent_delete_after_days": 365
        },
        "auto_backup": {
            "enabled": True,
            "backup_frequency_hours": 6,
            "backup_retention_days": 30,
            "offsite_backup_enabled": True
        }
    }

    # Performance and SLA configurations
    PERFORMANCE_TARGETS = {
        "processing_time_sla": {
            ContentCategory.MUSIC_ORIGINAL: 300,  # seconds
            ContentCategory.VIDEO_ORIGINAL: 1800,  # seconds
            ContentCategory.IMAGE_PHOTOGRAPHY: 60,  # seconds
            ContentCategory.TEXT_BLOG: 30  # seconds
        },
        "availability_sla": 99.95,  # percentage
        "response_time_sla": 200,  # milliseconds
        "concurrent_processing_limit": 100,
        "queue_processing_rate": 50,  # items per minute
        "error_rate_threshold": 0.01  # 1%
    }

    @classmethod
    def get_valid_transitions(cls, current_status: ContentStatus) -> List[StateTransition]:
        """Get valid state transitions from current status."""
        return [t for t in cls.STATE_TRANSITIONS if t.from_state == current_status]

    @classmethod
    def can_transition(cls, current_status: ContentStatus, target_status: ContentStatus, 
                      user_permissions: Set[str], conditions: Dict[str, bool]) -> Tuple[bool, str]:
        """Check if a state transition is valid."""
        valid_transitions = cls.get_valid_transitions(current_status)
        
        for transition in valid_transitions:
            if transition.to_state == target_status:
                # Check permissions
                if not transition.required_permissions.issubset(user_permissions):
                    return False, "Insufficient permissions"
                
                # Check conditions
                for condition, expected_value in transition.conditions.items():
                    if conditions.get(condition) != expected_value:
                        return False, f"Condition not met: {condition}"
                
                return True, "Valid transition"
        
        return False, "Invalid transition"

    @classmethod
    def get_status_config(cls, status: ContentStatus) -> Dict:
        """Get configuration for a specific content status."""
        return cls.STATUS_CONFIGS.get(status, {})

    @classmethod
    def get_category_rules(cls, category: ContentCategory) -> Dict:
        """Get business rules for a specific content category."""
        return cls.CATEGORY_RULES.get(category, {})

    @classmethod
    def is_status_expired(cls, status: ContentStatus, created_at: datetime) -> bool:
        """Check if content in current status has exceeded time limits."""
        config = cls.get_status_config(status)
        
        if "max_duration_days" in config and config["max_duration_days"] > 0:
            expiry_date = created_at + timedelta(days=config["max_duration_days"])
            return datetime.utcnow() > expiry_date
        
        if "max_duration_hours" in config and config["max_duration_hours"] > 0:
            expiry_date = created_at + timedelta(hours=config["max_duration_hours"])
            return datetime.utcnow() > expiry_date
        
        return False

    @classmethod
    def get_auto_transitions(cls) -> List[StateTransition]:
        """Get all automatic state transitions."""
        return [t for t in cls.STATE_TRANSITIONS if t.auto_transition]

    @classmethod
    def requires_review(cls, status: ContentStatus) -> bool:
        """Check if status requires manual review."""
        config = cls.get_status_config(status)
        return config.get("review_required", False)

    @classmethod
    def is_publicly_visible(cls, status: ContentStatus) -> bool:
        """Check if content in status is publicly visible."""
        config = cls.get_status_config(status)
        return config.get("visible", False)

    @classmethod
    def get_processing_priority(cls, category: ContentCategory, user_tier: str) -> ContentPriority:
        """Determine processing priority based on content category and user tier."""
        base_priority = ContentPriority.NORMAL
        
        if category in [ContentCategory.MUSIC_ORIGINAL, ContentCategory.VIDEO_ORIGINAL]:
            base_priority = ContentPriority.HIGH
        
        if user_tier in ["enterprise", "professional"]:
            if base_priority == ContentPriority.HIGH:
                return ContentPriority.ULTRA_HIGH
            else:
                return ContentPriority.HIGH
        
        return base_priority
