"""Workflow Configuration Module
============================

Manages multi-format content processing workflows and business logic flows.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""from enum import Enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content type enumeration for workflow processing."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    MIXED_MEDIA = "mixed_media"


class WorkflowStage(str, Enum):
    """Workflow processing stages."""    UPLOAD = "upload"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    FINGERPRINTING = "fingerprinting"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingPriority(str, Enum):
    """Processing priority levels."""    ULTRA_HIGH = "ultra_high"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class StageConfiguration:
    """Configuration for workflow stage."""    name: str
    timeout_seconds: int
    retry_attempts: int
    parallel_processing: bool
    required_services: List[str]
    optional_services: List[str]
    failure_strategy: str
    success_criteria: Dict[str, Union[str, int, float]]


class WorkflowConfig:
    """Enterprise workflow configuration management."""    # Content processing workflows
    CONTENT_WORKFLOWS = {
        ContentType.AUDIO: {
            "stages": [
                WorkflowStage.UPLOAD,
                WorkflowStage.VALIDATION,
                WorkflowStage.PREPROCESSING,
                WorkflowStage.FINGERPRINTING,
                WorkflowStage.PROTECTION,
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION,
                WorkflowStage.MONETIZATION,
                WorkflowStage.MONITORING
            ],
            "priority": ProcessingPriority.HIGH,
            "max_processing_time": 3600,
            "parallel_stages": [
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING
            ]
        },
        ContentType.VIDEO: {
            "stages": [
                WorkflowStage.UPLOAD,
                WorkflowStage.VALIDATION,
                WorkflowStage.PREPROCESSING,
                WorkflowStage.FINGERPRINTING,
                WorkflowStage.PROTECTION,
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION,
                WorkflowStage.MONETIZATION,
                WorkflowStage.MONITORING
            ],
            "priority": ProcessingPriority.HIGH,
            "max_processing_time": 7200,
            "parallel_stages": [
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING
            ]
        },
        ContentType.IMAGE: {
            "stages": [
                WorkflowStage.UPLOAD,
                WorkflowStage.VALIDATION,
                WorkflowStage.PREPROCESSING,
                WorkflowStage.FINGERPRINTING,
                WorkflowStage.PROTECTION,
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION,
                WorkflowStage.MONETIZATION,
                WorkflowStage.MONITORING
            ],
            "priority": ProcessingPriority.NORMAL,
            "max_processing_time": 1800,
            "parallel_stages": [
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION
            ]
        },
        ContentType.TEXT: {
            "stages": [
                WorkflowStage.UPLOAD,
                WorkflowStage.VALIDATION,
                WorkflowStage.PREPROCESSING,
                WorkflowStage.FINGERPRINTING,
                WorkflowStage.PROTECTION,
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION,
                WorkflowStage.MONETIZATION,
                WorkflowStage.MONITORING
            ],
            "priority": ProcessingPriority.NORMAL,
            "max_processing_time": 900,
            "parallel_stages": [
                WorkflowStage.SEO_OPTIMIZATION,
                WorkflowStage.COLLABORATION_MATCHING,
                WorkflowStage.DISTRIBUTION
            ]
        }
    }

    # Stage configurations
    STAGE_CONFIGURATIONS = {
        WorkflowStage.UPLOAD: StageConfiguration(
            name="Content Upload",
            timeout_seconds=300,
            retry_attempts=3,
            parallel_processing=True,
            required_services=["storage", "validation"],
            optional_services=["virus_scan"],
            failure_strategy="retry_with_delay",
            success_criteria={"file_integrity": "passed", "size_limit": "within_bounds"}
        ),
        WorkflowStage.VALIDATION: StageConfiguration(
            name="Content Validation",
            timeout_seconds=120,
            retry_attempts=2,
            parallel_processing=True,
            required_services=["format_validator", "content_analyzer"],
            optional_services=["compliance_checker"],
            failure_strategy="fail_fast",
            success_criteria={"format_valid": True, "content_appropriate": True}
        ),
        WorkflowStage.PREPROCESSING: StageConfiguration(
            name="Content Preprocessing",
            timeout_seconds=600,
            retry_attempts=3,
            parallel_processing=False,
            required_services=["media_processor", "metadata_extractor"],
            optional_services=["thumbnail_generator", "preview_generator"],
            failure_strategy="retry_with_exponential_backoff",
            success_criteria={"processing_complete": True, "quality_maintained": True}
        ),
        WorkflowStage.FINGERPRINTING: StageConfiguration(
            name="AI Fingerprinting",
            timeout_seconds=900,
            retry_attempts=3,
            parallel_processing=False,
            required_services=["fingerprint_engine", "vector_store"],
            optional_services=["similarity_checker"],
            failure_strategy="retry_with_exponential_backoff",
            success_criteria={"fingerprint_generated": True, "vector_stored": True}
        ),
        WorkflowStage.PROTECTION: StageConfiguration(
            name="Content Protection",
            timeout_seconds=300,
            retry_attempts=3,
            parallel_processing=True,
            required_services=["protection_engine", "license_manager"],
            optional_services=["watermark_generator"],
            failure_strategy="retry_with_delay",
            success_criteria={"protection_applied": True, "license_registered": True}
        ),
        WorkflowStage.SEO_OPTIMIZATION: StageConfiguration(
            name="SEO Optimization",
            timeout_seconds=180,
            retry_attempts=2,
            parallel_processing=True,
            required_services=["seo_analyzer", "keyword_extractor"],
            optional_services=["trend_analyzer", "hashtag_generator"],
            failure_strategy="continue_on_failure",
            success_criteria={"keywords_extracted": True, "metadata_optimized": True}
        ),
        WorkflowStage.COLLABORATION_MATCHING: StageConfiguration(
            name="Collaboration Matching",
            timeout_seconds=240,
            retry_attempts=2,
            parallel_processing=True,
            required_services=["matching_engine", "user_profiler"],
            optional_services=["recommendation_engine"],
            failure_strategy="continue_on_failure",
            success_criteria={"matches_found": ">=1", "compatibility_score": ">0.7"}
        ),
        WorkflowStage.DISTRIBUTION: StageConfiguration(
            name="Multi-Platform Distribution",
            timeout_seconds=1200,
            retry_attempts=5,
            parallel_processing=True,
            required_services=["distribution_manager", "platform_connectors"],
            optional_services=["schedule_optimizer"],
            failure_strategy="partial_success_allowed",
            success_criteria={"platforms_reached": ">=50%", "api_responses": "success"}
        ),
        WorkflowStage.MONETIZATION: StageConfiguration(
            name="Monetization Setup",
            timeout_seconds=300,
            retry_attempts=3,
            parallel_processing=True,
            required_services=["payment_processor", "revenue_tracker"],
            optional_services=["pricing_optimizer"],
            failure_strategy="retry_with_delay",
            success_criteria={"payment_configured": True, "tracking_enabled": True}
        ),
        WorkflowStage.MONITORING: StageConfiguration(
            name="Content Monitoring",
            timeout_seconds=60,
            retry_attempts=1,
            parallel_processing=True,
            required_services=["monitoring_service", "alert_manager"],
            optional_services=["analytics_collector"],
            failure_strategy="continue_on_failure",
            success_criteria={"monitoring_active": True, "alerts_configured": True}
        )
    }

    # Creator type specific workflows
    CREATOR_WORKFLOWS = {
        "musician": {
            "primary_content": [ContentType.AUDIO, ContentType.VIDEO],
            "secondary_content": [ContentType.IMAGE, ContentType.TEXT],
            "processing_priority": ProcessingPriority.ULTRA_HIGH,
            "special_stages": ["spotify_integration", "music_metadata_enrichment"],
            "monetization_focus": ["streaming_revenue", "licensing", "merchandise"]
        },
        "blogger": {
            "primary_content": [ContentType.TEXT, ContentType.IMAGE],
            "secondary_content": [ContentType.VIDEO, ContentType.AUDIO],
            "processing_priority": ProcessingPriority.HIGH,
            "special_stages": ["seo_enhancement", "social_media_optimization"],
            "monetization_focus": ["advertising", "affiliate", "subscriptions"]
        },
        "photographer": {
            "primary_content": [ContentType.IMAGE],
            "secondary_content": [ContentType.VIDEO, ContentType.TEXT],
            "processing_priority": ProcessingPriority.HIGH,
            "special_stages": ["image_quality_enhancement", "portfolio_optimization"],
            "monetization_focus": ["licensing", "print_sales", "commissions"]
        },
        "influencer": {
            "primary_content": [ContentType.VIDEO, ContentType.IMAGE],
            "secondary_content": [ContentType.TEXT, ContentType.LIVESTREAM],
            "processing_priority": ProcessingPriority.ULTRA_HIGH,
            "special_stages": ["virality_prediction", "engagement_optimization"],
            "monetization_focus": ["sponsorships", "brand_partnerships", "merchandise"]
        },
        "comedian": {
            "primary_content": [ContentType.VIDEO, ContentType.AUDIO],
            "secondary_content": [ContentType.TEXT, ContentType.IMAGE],
            "processing_priority": ProcessingPriority.HIGH,
            "special_stages": ["comedy_timing_analysis", "audience_sentiment"],
            "monetization_focus": ["show_bookings", "streaming", "merchandise"]
        },
        "podcaster": {
            "primary_content": [ContentType.PODCAST, ContentType.AUDIO],
            "secondary_content": [ContentType.VIDEO, ContentType.TEXT],
            "processing_priority": ProcessingPriority.HIGH,
            "special_stages": ["transcript_generation", "episode_optimization"],
            "monetization_focus": ["sponsorships", "subscriptions", "premium_content"]
        }
    }

    # Business rule configurations
    BUSINESS_RULES = {
        "content_validation": {
            "max_file_size": {
                ContentType.AUDIO: 500 * 1024 * 1024,  # 500MB
                ContentType.VIDEO: 2 * 1024 * 1024 * 1024,  # 2GB
                ContentType.IMAGE: 50 * 1024 * 1024,  # 50MB
                ContentType.TEXT: 10 * 1024 * 1024,  # 10MB
            },
            "allowed_formats": {
                ContentType.AUDIO: ["mp3", "wav", "flac", "aac", "m4a"],
                ContentType.VIDEO: ["mp4", "avi", "mov", "mkv", "webm"],
                ContentType.IMAGE: ["jpg", "jpeg", "png", "gif", "svg", "webp"],
                ContentType.TEXT: ["txt", "md", "html", "pdf", "docx"],
            },
            "quality_requirements": {
                "audio_bitrate_min": 128000,
                "video_resolution_min": "720p",
                "image_resolution_min": "1920x1080",
                "text_readability_score": 60
            }
        },
        "protection_policies": {
            "fingerprint_sensitivity": 0.85,
            "similarity_threshold": 0.9,
            "protection_duration_days": 365 * 5,  # 5 years
            "monitoring_frequency_hours": 6,
            "alert_threshold_matches": 3
        },
        "monetization_rules": {
            "revenue_share_percentage": 85,  # Creator gets 85%
            "minimum_payout_amount": 50.0,
            "payout_frequency_days": 30,
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"],
            "tax_compliance_required": True
        },
        "collaboration_matching": {
            "compatibility_score_min": 0.7,
            "max_matches_per_request": 20,
            "matching_criteria_weights": {
                "genre_similarity": 0.3,
                "audience_overlap": 0.25,
                "location_proximity": 0.15,
                "experience_level": 0.15,
                "collaboration_history": 0.15
            }
        }
    }

    # SLA and performance targets
    SLA_TARGETS = {
        "processing_time": {
            ContentType.AUDIO: 300,  # seconds
            ContentType.VIDEO: 1800,  # seconds
            ContentType.IMAGE: 60,   # seconds
            ContentType.TEXT: 30,    # seconds
        },
        "uptime_percentage": 99.95,
        "api_response_time_ms": 200,
        "fingerprint_accuracy": 0.95,
        "false_positive_rate": 0.05,
        "availability_zones": 3,
        "backup_frequency_hours": 6
    }

    @classmethod
    def get_workflow_for_content_type(cls, content_type: ContentType) -> Dict:
        """Get workflow configuration for specific content type."""        return cls.CONTENT_WORKFLOWS.get(content_type, cls.CONTENT_WORKFLOWS[ContentType.TEXT])

    @classmethod
    def get_creator_workflow(cls, creator_type: str) -> Dict:
        """Get workflow configuration for specific creator type."""        return cls.CREATOR_WORKFLOWS.get(creator_type.lower(), cls.CREATOR_WORKFLOWS["influencer"])

    @classmethod
    def get_stage_config(cls, stage: WorkflowStage) -> StageConfiguration:
        """Get configuration for specific workflow stage."""        return cls.STAGE_CONFIGURATIONS.get(stage)

    @classmethod
    def validate_business_rules(cls, content_type: ContentType, file_size: int, format_type: str) -> bool:
        """Validate content against business rules."""        max_size = cls.BUSINESS_RULES["content_validation"]["max_file_size"].get(content_type, 0)
        allowed_formats = cls.BUSINESS_RULES["content_validation"]["allowed_formats"].get(content_type, [])
        
        return file_size <= max_size and format_type.lower() in allowed_formats

    @classmethod
    def get_processing_priority(cls, creator_type: str, content_type: ContentType) -> ProcessingPriority:
        """Determine processing priority based on creator and content type."""        creator_config = cls.get_creator_workflow(creator_type)
        
        if content_type in creator_config.get("primary_content", []):
            return creator_config.get("processing_priority", ProcessingPriority.NORMAL)
        
        return ProcessingPriority.NORMAL
