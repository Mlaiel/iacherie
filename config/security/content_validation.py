"""Content Validation Configuration Module
=======================================

Advanced content validation and security scanning configuration for 
IA Influencer Agent platform. Provides comprehensive content security,
malware detection, and content policy enforcement.

Business Logic Integration:
- Content validation before IA processing pipeline
- Multi-format security scanning for creators
- Copyright compliance validation
- Platform-specific content policy enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class ContentType(Enum):
    """Supported content types for validation."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    METADATA = "metadata"


class ValidationSeverity(Enum):
    """Validation result severity levels."""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class ThreatType(Enum):
    """Types of security threats to detect."""    MALWARE = "malware"
    VIRUS = "virus"
    TROJAN = "trojan"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    SPAM = "spam"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    COPYRIGHT_VIOLATION = "copyright_violation"
    DEEPFAKE = "deepfake"
    SUSPICIOUS_SCRIPT = "suspicious_script"


class ScanEngine(Enum):
    """Available scanning engines."""    CLAMAV = "clamav"
    VIRUSTOTAL = "virustotal"
    WINDOWS_DEFENDER = "windows_defender"
    YARA = "yara"
    CUSTOM_ML = "custom_ml"
    CONTENT_MODERATOR = "content_moderator"


@dataclass
class FileTypeValidation:
    """File type specific validation rules."""    allowed_extensions: Set[str] = field(default_factory=set)
    max_file_size_mb: int = 100
    mime_type_validation: bool = True
    magic_number_validation: bool = True
    
    # Content-specific validations
    dimension_limits: Optional[Dict[str, int]] = None  # width, height for images/videos
    duration_limits: Optional[Dict[str, int]] = None   # min, max duration for audio/video
    bitrate_limits: Optional[Dict[str, int]] = None    # min, max bitrate
    
    # Security validations
    embedded_content_scan: bool = True
    metadata_sanitization: bool = True
    steganography_detection: bool = False


@dataclass
class AudioValidationConfig:
    """Audio-specific validation configuration."""    allowed_formats: Set[str] = field(default_factory=lambda: {
        "mp3", "wav", "flac", "ogg", "m4a", "aac", "wma"
    })
    max_file_size_mb: int = 500
    max_duration_minutes: int = 60
    min_duration_seconds: int = 1
    
    # Audio quality validation
    min_bitrate_kbps: int = 96
    max_bitrate_kbps: int = 320
    sample_rate_validation: bool = True
    allowed_sample_rates: Set[int] = field(default_factory=lambda: {
        8000, 11025, 16000, 22050, 44100, 48000, 96000
    })
    
    # Content validation
    silence_detection: bool = True
    max_silence_percentage: float = 30.0
    audio_fingerprint_validation: bool = True
    copyrighted_content_detection: bool = True
    
    # Format-specific validation
    mp3_validation: Dict[str, Any] = field(default_factory=lambda: {
        "id3_tag_validation": True,
        "frame_validation": True,
        "corruption_detection": True
    })


@dataclass
class VideoValidationConfig:
    """Video-specific validation configuration."""    allowed_formats: Set[str] = field(default_factory=lambda: {
        "mp4", "avi", "mov", "wmv", "mkv", "webm", "flv"
    })
    max_file_size_mb: int = 2048  # 2GB
    max_duration_minutes: int = 120
    min_duration_seconds: int = 1
    
    # Video quality validation
    max_resolution: Dict[str, int] = field(default_factory=lambda: {
        "width": 3840,   # 4K
        "height": 2160
    })
    min_resolution: Dict[str, int] = field(default_factory=lambda: {
        "width": 640,
        "height": 480
    })
    
    # Frame rate validation
    min_fps: float = 15.0
    max_fps: float = 120.0
    
    # Content validation
    inappropriate_content_detection: bool = True
    deepfake_detection: bool = True
    violence_detection: bool = True
    adult_content_detection: bool = True
    
    # Codec validation
    allowed_video_codecs: Set[str] = field(default_factory=lambda: {
        "h264", "h265", "vp8", "vp9", "av1"
    })
    allowed_audio_codecs: Set[str] = field(default_factory=lambda: {
        "aac", "mp3", "opus", "vorbis"
    })


@dataclass
class ImageValidationConfig:
    """Image-specific validation configuration."""    allowed_formats: Set[str] = field(default_factory=lambda: {
        "jpg", "jpeg", "png", "gif", "webp", "tiff", "bmp"
    })
    max_file_size_mb: int = 50
    
    # Image dimensions validation
    max_dimensions: Dict[str, int] = field(default_factory=lambda: {
        "width": 8192,
        "height": 8192
    })
    min_dimensions: Dict[str, int] = field(default_factory=lambda: {
        "width": 100,
        "height": 100
    })
    
    # Image quality validation
    min_dpi: Optional[int] = None
    max_dpi: Optional[int] = None
    color_depth_validation: bool = True
    
    # Content validation
    inappropriate_content_detection: bool = True
    face_detection: bool = True
    nudity_detection: bool = True
    violence_detection: bool = True
    
    # Technical validation
    exif_data_sanitization: bool = True
    embedded_thumbnail_validation: bool = True
    color_profile_validation: bool = True


@dataclass
class TextValidationConfig:
    """Text content validation configuration."""    max_length_chars: int = 1000000  # 1M characters
    encoding_validation: bool = True
    allowed_encodings: Set[str] = field(default_factory=lambda: {
        "utf-8", "utf-16", "ascii", "iso-8859-1"
    })
    
    # Content validation
    profanity_detection: bool = True
    hate_speech_detection: bool = True
    spam_detection: bool = True
    phishing_detection: bool = True
    
    # Language validation
    language_detection: bool = True
    allowed_languages: Optional[Set[str]] = None  # None means all allowed
    
    # Format validation
    markdown_validation: bool = True
    html_sanitization: bool = True
    script_injection_detection: bool = True
    
    # Copyright validation
    plagiarism_detection: bool = True
    copyright_text_detection: bool = True


@dataclass
class MalwareScanningConfig:
    """Malware and virus scanning configuration."""    enabled: bool = True
    scan_engines: List[ScanEngine] = field(default_factory=lambda: [
        ScanEngine.CLAMAV,
        ScanEngine.YARA,
        ScanEngine.CUSTOM_ML
    ])
    
    # ClamAV configuration
    clamav_config: Dict[str, Any] = field(default_factory=lambda: {
        "daemon_host": "localhost",
        "daemon_port": 3310,
        "socket_path": "/var/run/clamav/clamd.ctl",
        "database_update_frequency": "daily",
        "signature_timeout": 30
    })
    
    # VirusTotal configuration
    virustotal_config: Dict[str, Any] = field(default_factory=lambda: {
        "api_key": os.getenv("VIRUSTOTAL_API_KEY", ""),
        "scan_timeout": 300,
        "minimum_detections": 2,
        "upload_enabled": False  # Privacy consideration
    })
    
    # YARA rules configuration
    yara_config: Dict[str, Any] = field(default_factory=lambda: {
        "rules_directory": "/opt/yara-rules",
        "custom_rules_enabled": True,
        "rule_update_frequency": "weekly",
        "scan_timeout": 60
    })
    
    # Custom ML scanning
    custom_ml_config: Dict[str, Any] = field(default_factory=lambda: {
        "model_path": "/opt/malware-detection/model",
        "confidence_threshold": 0.8,
        "feature_extraction": "static_analysis",
        "real_time_updates": True
    })
    
    # Quarantine configuration
    quarantine_enabled: bool = True
    quarantine_path: str = "/var/quarantine/ia-influencer"
    quarantine_retention_days: int = 30


@dataclass
class ContentModerationConfig:
    """Content moderation and policy enforcement configuration."""    enabled: bool = True
    
    # Platform-specific policies
    platform_policies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "spotify": {
            "explicit_content": "warn",
            "copyright_strict": True,
            "quality_requirements": "high"
        },
        "youtube": {
            "community_guidelines": True,
            "age_restriction_check": True,
            "monetization_friendly": True
        },
        "instagram": {
            "community_standards": True,
            "nudity_detection": True,
            "violence_detection": True
        },
        "tiktok": {
            "community_guidelines": True,
            "minor_safety": True,
            "dangerous_behavior": True
        }
    })
    
    # AI-based moderation
    ai_moderation_enabled: bool = True
    ai_confidence_threshold: float = 0.85
    
    # Manual review configuration
    manual_review_enabled: bool = True
    escalation_threshold: float = 0.7
    review_queue_priority: List[str] = field(default_factory=lambda: [
        "copyright_violation",
        "inappropriate_content", 
        "deepfake",
        "hate_speech"
    ])
    
    # Content categories
    content_categories: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "safe": {"action": "allow", "confidence_required": 0.9},
        "questionable": {"action": "review", "confidence_required": 0.7},
        "inappropriate": {"action": "block", "confidence_required": 0.8},
        "harmful": {"action": "block", "confidence_required": 0.6}
    })


@dataclass
class CopyrightValidationConfig:
    """Copyright and intellectual property validation configuration."""    enabled: bool = True
    
    # Content identification
    audio_fingerprinting: bool = True
    video_fingerprinting: bool = True
    image_fingerprinting: bool = True
    text_similarity_detection: bool = True
    
    # Database configurations
    copyright_databases: List[str] = field(default_factory=lambda: [
        "internal_fingerprints",
        "audible_magic",
        "gracenote",
        "youtube_content_id"
    ])
    
    # Matching thresholds
    audio_match_threshold: float = 0.85
    video_match_threshold: float = 0.80
    image_match_threshold: float = 0.90
    text_similarity_threshold: float = 0.75
    
    # Fair use detection
    fair_use_analysis: bool = True
    transformative_use_detection: bool = True
    commentary_detection: bool = True
    parody_detection: bool = True
    
    # DMCA compliance
    dmca_compliance: bool = True
    takedown_automation: bool = True
    counter_notification_support: bool = True
    
    # Rights management
    creative_commons_validation: bool = True
    licensing_verification: bool = True
    attribution_checking: bool = True


@dataclass
class PerformanceOptimization:
    """Validation performance optimization configuration."""    
    # Parallel processing
    parallel_validation: bool = True
    max_worker_threads: int = 8
    thread_pool_size: int = 16
    
    # Caching
    validation_cache_enabled: bool = True
    cache_ttl_hours: int = 24
    cache_size_mb: int = 512
    
    # Progressive scanning
    progressive_scan_enabled: bool = True
    quick_scan_first: bool = True
    full_scan_threshold_mb: int = 100
    
    # Resource limits
    max_memory_usage_mb: int = 2048
    max_cpu_usage_percent: int = 80
    scan_timeout_seconds: int = 300
    
    # Optimization strategies
    skip_duplicate_scans: bool = True
    intelligent_prioritization: bool = True
    adaptive_scanning: bool = True


@dataclass
class ValidationReporting:
    """Validation results reporting configuration."""    
    # Report generation
    detailed_reports: bool = True
    summary_reports: bool = True
    real_time_alerts: bool = True
    
    # Report formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "json", "xml", "pdf", "html"
    ])
    
    # Alert configuration
    alert_channels: List[str] = field(default_factory=lambda: [
        "email", "webhook", "slack", "database"
    ])
    
    # Severity-based reporting
    report_thresholds: Dict[ValidationSeverity, bool] = field(default_factory=lambda: {
        ValidationSeverity.INFO: False,
        ValidationSeverity.WARNING: True,
        ValidationSeverity.ERROR: True,
        ValidationSeverity.CRITICAL: True,
        ValidationSeverity.BLOCKED: True
    })
    
    # Historical tracking
    track_validation_trends: bool = True
    trend_analysis_days: int = 30
    performance_metrics: bool = True


@dataclass
class ContentValidationConfig:
    """Main content validation configuration container."""    
    # Type-specific configurations
    audio: AudioValidationConfig = field(default_factory=AudioValidationConfig)
    video: VideoValidationConfig = field(default_factory=VideoValidationConfig)
    image: ImageValidationConfig = field(default_factory=ImageValidationConfig)
    text: TextValidationConfig = field(default_factory=TextValidationConfig)
    
    # Security configurations
    malware_scanning: MalwareScanningConfig = field(default_factory=MalwareScanningConfig)
    content_moderation: ContentModerationConfig = field(default_factory=ContentModerationConfig)
    copyright_validation: CopyrightValidationConfig = field(default_factory=CopyrightValidationConfig)
    
    # Performance and reporting
    performance: PerformanceOptimization = field(default_factory=PerformanceOptimization)
    reporting: ValidationReporting = field(default_factory=ValidationReporting)
    
    # Global validation settings
    validation_enabled: bool = True
    strict_mode: bool = True
    fail_on_first_error: bool = False
    
    # Creator tier-based validation
    tier_based_validation: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "free": {
            "max_file_size_mb": 50,
            "basic_scanning": True,
            "advanced_features": False
        },
        "basic": {
            "max_file_size_mb": 200,
            "basic_scanning": True,
            "advanced_features": True,
            "priority_processing": False
        },
        "professional": {
            "max_file_size_mb": 1000,
            "basic_scanning": True,
            "advanced_features": True,
            "priority_processing": True,
            "custom_rules": True
        },
        "enterprise": {
            "max_file_size_mb": -1,  # unlimited
            "basic_scanning": True,
            "advanced_features": True,
            "priority_processing": True,
            "custom_rules": True,
            "dedicated_resources": True
        }
    })
    
    # Integration settings
    webhook_notifications: bool = True
    api_integration: bool = True
    real_time_processing: bool = True
    
    # Compliance settings
    gdpr_compliance: bool = True
    data_retention_days: int = 90
    audit_trail: bool = True


# Default configuration instance
content_validation_config = ContentValidationConfig()


def get_content_validation_config() -> ContentValidationConfig:
    """Get the content validation configuration instance."""    return content_validation_config


def get_validation_config_for_content_type(content_type: ContentType) -> Any:
    """Get validation configuration for specific content type."""    config = get_content_validation_config()
    
    mapping = {
        ContentType.AUDIO: config.audio,
        ContentType.VIDEO: config.video,
        ContentType.IMAGE: config.image,
        ContentType.TEXT: config.text,
        ContentType.DOCUMENT: config.text,  # Use text config for documents
        ContentType.METADATA: config.text,  # Use text config for metadata
    }
    
    return mapping.get(content_type, config.text)


def get_tier_validation_settings(tier: str) -> Dict[str, Any]:
    """Get validation settings for specific subscription tier."""    config = get_content_validation_config()
    return config.tier_based_validation.get(tier, config.tier_based_validation["basic"])


def validate_content_validation_config(config: ContentValidationConfig) -> bool:
    """Validate content validation configuration settings."""    # Validate file size limits
    for content_config in [config.audio, config.video, config.image]:
        if hasattr(content_config, 'max_file_size_mb') and content_config.max_file_size_mb <= 0:
            raise ValueError(f"Invalid max file size: {content_config.max_file_size_mb}")
    
    # Validate threshold values
    if not (0 <= config.copyright_validation.audio_match_threshold <= 1):
        raise ValueError("Audio match threshold must be between 0 and 1")
    
    # Validate scan engines
    if not config.malware_scanning.scan_engines:
        raise ValueError("At least one scan engine must be configured")
    
    return True
