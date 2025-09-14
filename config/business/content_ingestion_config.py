"""
Content Ingestion Configuration - Enterprise Configuration Management
Enterprise configuration for content ingestion and validation systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


class IngestionMethod(str, Enum):
    """Content ingestion methods"""
    UPLOAD = "upload"
    API = "api"
    WEBHOOK = "webhook"
    BULK_IMPORT = "bulk_import"
    STREAMING = "streaming"
    AUTOMATED_CRAWL = "automated_crawl"


class ValidationLevel(str, Enum):
    """Content validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class ProcessingPriority(str, Enum):
    """Content processing priorities"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"


class ContentStatus(str, Enum):
    """Content ingestion status"""
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    QUARANTINED = "quarantined"


@dataclass
class FileSizeLimit:
    """File size limits configuration"""
    max_size_bytes: int
    max_size_human: str
    recommended_size_bytes: int
    warning_threshold_bytes: int


@dataclass
class QualityStandard:
    """Quality standards configuration"""
    minimum_resolution: str
    recommended_resolution: str
    minimum_bitrate: str
    color_depth: str
    codec_requirements: List[str]
    metadata_requirements: List[str]


@dataclass
class ValidationRule:
    """Content validation rule"""
    rule_name: str
    rule_type: str
    enabled: bool
    severity: str
    parameters: Dict[str, Any]
    error_message: str


@dataclass
class IngestionWorkflow:
    """Content ingestion workflow configuration"""
    workflow_name: str
    steps: List[str]
    validation_points: List[str]
    error_handling: str
    retry_policy: Dict[str, Any]
    timeout_seconds: int


class ContentIngestionSettings:
    """Content ingestion configuration settings"""
    
    def __init__(self) -> None:
        # File Size Limits by Content Type
        self.file_size_limits = {
            "audio": FileSizeLimit(
                max_size_bytes=500 * 1024 * 1024,  # 500MB
                max_size_human="500MB",
                recommended_size_bytes=100 * 1024 * 1024,  # 100MB
                warning_threshold_bytes=300 * 1024 * 1024  # 300MB
            ),
            "video": FileSizeLimit(
                max_size_bytes=2 * 1024 * 1024 * 1024,  # 2GB
                max_size_human="2GB",
                recommended_size_bytes=500 * 1024 * 1024,  # 500MB
                warning_threshold_bytes=1024 * 1024 * 1024  # 1GB
            ),
            "image": FileSizeLimit(
                max_size_bytes=50 * 1024 * 1024,  # 50MB
                max_size_human="50MB",
                recommended_size_bytes=10 * 1024 * 1024,  # 10MB
                warning_threshold_bytes=25 * 1024 * 1024  # 25MB
            ),
            "text": FileSizeLimit(
                max_size_bytes=10 * 1024 * 1024,  # 10MB
                max_size_human="10MB",
                recommended_size_bytes=1024 * 1024,  # 1MB
                warning_threshold_bytes=5 * 1024 * 1024  # 5MB
            ),
            "voice": FileSizeLimit(
                max_size_bytes=100 * 1024 * 1024,  # 100MB
                max_size_human="100MB",
                recommended_size_bytes=20 * 1024 * 1024,  # 20MB
                warning_threshold_bytes=50 * 1024 * 1024  # 50MB
            ),
            "avatar": FileSizeLimit(
                max_size_bytes=200 * 1024 * 1024,  # 200MB
                max_size_human="200MB",
                recommended_size_bytes=50 * 1024 * 1024,  # 50MB
                warning_threshold_bytes=100 * 1024 * 1024  # 100MB
            )
        }
        
        # Quality Standards by Content Type
        self.quality_standards = {
            "audio": QualityStandard(
                minimum_resolution="16-bit/44.1kHz",
                recommended_resolution="24-bit/48kHz",
                minimum_bitrate="320kbps",
                color_depth="N/A",
                codec_requirements=["MP3", "WAV", "FLAC", "AAC"],
                metadata_requirements=["title", "artist", "duration", "format"]
            ),
            "video": QualityStandard(
                minimum_resolution="1080p",
                recommended_resolution="4K",
                minimum_bitrate="5Mbps",
                color_depth="8-bit minimum",
                codec_requirements=["H.264", "H.265", "VP9"],
                metadata_requirements=["title", "duration", "resolution", "framerate", "codec"]
            ),
            "image": QualityStandard(
                minimum_resolution="2048x2048",
                recommended_resolution="4096x4096",
                minimum_bitrate="N/A",
                color_depth="24-bit minimum",
                codec_requirements=["JPEG", "PNG", "TIFF", "WebP"],
                metadata_requirements=["dimensions", "format", "color_space", "dpi"]
            ),
            "text": QualityStandard(
                minimum_resolution="Grade 8 readability",
                recommended_resolution="Professional writing standard",
                minimum_bitrate="N/A",
                color_depth="N/A",
                codec_requirements=["UTF-8", "Markdown", "HTML", "PDF"],
                metadata_requirements=["title", "word_count", "language", "encoding"]
            )
        }
        
        # Validation Rules
        self.validation_rules = [
            ValidationRule(
                rule_name="copyright_check",
                rule_type="rights_verification",
                enabled=True,
                severity="critical",
                parameters={"fingerprint_match_threshold": 0.95, "database_check": True},
                error_message="Content may violate copyright. Please verify ownership rights."
            ),
            ValidationRule(
                rule_name="content_moderation",
                rule_type="safety_check",
                enabled=True,
                severity="high",
                parameters={"ai_moderation": True, "human_review_threshold": 0.8},
                error_message="Content flagged for inappropriate material."
            ),
            ValidationRule(
                rule_name="quality_assessment",
                rule_type="technical_validation",
                enabled=True,
                severity="medium",
                parameters={"auto_enhance": True, "quality_score_threshold": 0.7},
                error_message="Content does not meet minimum quality standards."
            ),
            ValidationRule(
                rule_name="metadata_extraction",
                rule_type="data_processing",
                enabled=True,
                severity="low",
                parameters={"extract_all": True, "verify_accuracy": True},
                error_message="Unable to extract required metadata."
            ),
            ValidationRule(
                rule_name="virus_scan",
                rule_type="security_check",
                enabled=True,
                severity="critical",
                parameters={"scan_engines": ["clamav", "defender"], "quarantine_on_detect": True},
                error_message="Content contains potential security threats."
            ),
            ValidationRule(
                rule_name="format_validation",
                rule_type="technical_validation",
                enabled=True,
                severity="high",
                parameters={"strict_validation": True, "auto_convert": False},
                error_message="Content format is not supported or corrupted."
            )
        ]
        
        # Ingestion Workflows
        self.ingestion_workflows = {
            "standard": IngestionWorkflow(
                workflow_name="Standard Content Ingestion",
                steps=[
                    "upload_validation",
                    "virus_scan",
                    "format_validation",
                    "quality_assessment",
                    "metadata_extraction",
                    "copyright_check",
                    "content_moderation",
                    "final_approval"
                ],
                validation_points=["upload_validation", "copyright_check", "content_moderation"],
                error_handling="retry_with_manual_review",
                retry_policy={
                    "max_retries": 3,
                    "backoff_strategy": "exponential",
                    "retry_delay_seconds": 60
                },
                timeout_seconds=1800  # 30 minutes
            ),
            "fast_track": IngestionWorkflow(
                workflow_name="Fast Track Ingestion",
                steps=[
                    "upload_validation",
                    "virus_scan",
                    "format_validation",
                    "auto_approval"
                ],
                validation_points=["upload_validation"],
                error_handling="immediate_rejection",
                retry_policy={
                    "max_retries": 1,
                    "backoff_strategy": "linear",
                    "retry_delay_seconds": 30
                },
                timeout_seconds=300  # 5 minutes
            ),
            "enterprise": IngestionWorkflow(
                workflow_name="Enterprise Grade Ingestion",
                steps=[
                    "upload_validation",
                    "virus_scan",
                    "format_validation",
                    "quality_assessment",
                    "metadata_extraction",
                    "copyright_check",
                    "content_moderation",
                    "ai_enhancement",
                    "compliance_check",
                    "manual_review",
                    "final_approval"
                ],
                validation_points=[
                    "upload_validation", 
                    "copyright_check", 
                    "content_moderation", 
                    "compliance_check",
                    "manual_review"
                ],
                error_handling="comprehensive_review",
                retry_policy={
                    "max_retries": 5,
                    "backoff_strategy": "exponential",
                    "retry_delay_seconds": 120
                },
                timeout_seconds=3600  # 60 minutes
            )
        }
        
        # Processing Settings
        self.concurrent_uploads_limit = 10
        self.batch_processing_size = 50
        self.processing_queue_priority = {
            ProcessingPriority.REAL_TIME: 1,
            ProcessingPriority.URGENT: 2,
            ProcessingPriority.HIGH: 3,
            ProcessingPriority.NORMAL: 4,
            ProcessingPriority.LOW: 5
        }
        
        # Storage Settings
        self.temporary_storage_duration_hours = 48
        self.backup_retention_days = 30
        self.cdn_distribution_enabled = True
        self.content_encryption_enabled = True
        
        # API Settings
        self.api_rate_limits = {
            "uploads_per_hour": 100,
            "uploads_per_day": 1000,
            "total_bandwidth_per_day": "10GB"
        }
        
        # Monitoring Settings
        self.ingestion_metrics_enabled = True
        self.real_time_monitoring = True
        self.alert_thresholds = {
            "failure_rate_percent": 5,
            "processing_delay_minutes": 30,
            "queue_size": 1000
        }
        
        # Business Logic Settings
        self.auto_categorization_enabled = True
        self.ai_enhancement_enabled = True
        self.smart_compression_enabled = True
        self.duplicate_detection_enabled = True
        
        # Compliance Settings
        self.gdpr_compliance_enabled = True
        self.data_retention_policy_days = 365
        self.audit_logging_enabled = True
        self.encryption_at_rest = True
    
    def get_file_size_limit(self, content_type: str) -> Optional[FileSizeLimit]:
        """Get file size limit for content type"""
        return self.file_size_limits.get(content_type)
    
    def get_quality_standard(self, content_type: str) -> Optional[QualityStandard]:
        """Get quality standard for content type"""
        return self.quality_standards.get(content_type)
    
    def get_workflow(self, workflow_name: str) -> Optional[IngestionWorkflow]:
        """Get ingestion workflow by name"""
        return self.ingestion_workflows.get(workflow_name)
    
    def is_file_size_valid(self, content_type: str, file_size_bytes: int) -> bool:
        """Check if file size is within limits"""
        limit = self.get_file_size_limit(content_type)
        return limit and file_size_bytes <= limit.max_size_bytes
    
    def get_enabled_validation_rules(self) -> List[ValidationRule]:
        """Get all enabled validation rules"""
        return [rule for rule in self.validation_rules if rule.enabled]
    
    def validate_content_type(self, content_type: str) -> bool:
        """Validate if content type is supported"""
        return content_type in self.file_size_limits
    
    def get_processing_timeout(self, workflow_name: str = "standard") -> int:
        """Get processing timeout for workflow"""
        workflow = self.get_workflow(workflow_name)
        return workflow.timeout_seconds if workflow else 1800
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete ingestion configuration"""
        errors = []
        
        # Validate file size limits
        for content_type, limit in self.file_size_limits.items():
            if limit.max_size_bytes <= 0:
                errors.append(f"Invalid max size for content type '{content_type}'")
            if limit.recommended_size_bytes > limit.max_size_bytes:
                errors.append(f"Recommended size exceeds max size for '{content_type}'")
        
        # Validate workflows
        for workflow_name, workflow in self.ingestion_workflows.items():
            if not workflow.steps:
                errors.append(f"Workflow '{workflow_name}' has no steps defined")
            if workflow.timeout_seconds <= 0:
                errors.append(f"Invalid timeout for workflow '{workflow_name}'")
        
        # Validate validation rules
        critical_rules = [rule for rule in self.validation_rules 
                         if rule.severity == "critical" and rule.enabled]
        if not critical_rules:
            errors.append("No critical validation rules enabled")
        
        return errors


# Global content ingestion settings instance
content_ingestion_settings = ContentIngestionSettings()

__all__ = [
    "ContentIngestionSettings",
    "content_ingestion_settings",
    "IngestionMethod",
    "ValidationLevel",
    "ProcessingPriority",
    "ContentStatus",
    "FileSizeLimit",
    "QualityStandard",
    "ValidationRule",
    "IngestionWorkflow"
]