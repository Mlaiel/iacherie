"""🏷️ Migration Types and Enumerations - Ultra-Industrial Type System
=================================================================
Module: backend/database/migrations/migration_types.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Type Definitions - Ultra Enterprise Production-Ready
Responsibility: Comprehensive type system for content protection and monetization migrations
==========================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Advanced type system supporting:
- Multi-modal content fingerprinting migration types
- Creator monetization database migration categories
- AI processing pipeline migration classifications
- Platform integration migration priorities
- Security and compliance migration types

TYPE CLASSIFICATION LOGIC:
Migration Request → Type Analysis → Priority Assignment → 
Category Classification → Risk Assessment → Execution Strategy Selection
"""

from enum import Enum, IntEnum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


class MigrationType(Enum):
    """
Comprehensive migration type classification for enterprise platform"""
    
    # Core schema migrations
    SCHEMA_CREATION = "schema_creation"
    SCHEMA_MODIFICATION = "schema_modification"
    SCHEMA_DELETION = "schema_deletion"
    
    # Data migrations
    DATA_MIGRATION = "data_migration"
    DATA_TRANSFORMATION = "data_transformation"
    DATA_CLEANUP = "data_cleanup"
    DATA_ARCHIVAL = "data_archival"
    
    # Index and performance migrations
    INDEX_CREATION = "index_creation"
    INDEX_MODIFICATION = "index_modification"
    INDEX_DELETION = "index_deletion"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    
    # Security migrations
    SECURITY_ENHANCEMENT = "security_enhancement"
    PERMISSION_UPDATE = "permission_update"
    ENCRYPTION_MIGRATION = "encryption_migration"
    
    # Content protection specific
    FINGERPRINT_SCHEMA = "fingerprint_schema"
    PROTECTION_RULES = "protection_rules"
    MONITORING_SETUP = "monitoring_setup"
    
    # Monetization specific
    REVENUE_TRACKING = "revenue_tracking"
    PAYMENT_INTEGRATION = "payment_integration"
    ANALYTICS_SCHEMA = "analytics_schema"
    
    # Platform integration
    PLATFORM_CONNECTOR = "platform_connector"
    API_INTEGRATION = "api_integration"
    WEBHOOK_SETUP = "webhook_setup"
    
    # AI and ML migrations
    ML_MODEL_DEPLOYMENT = "ml_model_deployment"
    VECTOR_STORE_SETUP = "vector_store_setup"
    AI_PIPELINE_CONFIG = "ai_pipeline_config"
    
    # Infrastructure migrations
    INFRASTRUCTURE_SETUP = "infrastructure_setup"
    MICROSERVICE_DEPLOYMENT = "microservice_deployment"
    MONITORING_CONFIG = "monitoring_config"
    
    # Emergency and rollback
    HOTFIX = "hotfix"
    EMERGENCY_PATCH = "emergency_patch"
    ROLLBACK = "rollback"
    RECOVERY = "recovery"
    
    # Maintenance
    MAINTENANCE = "maintenance"
    CLEANUP = "cleanup"
    OPTIMIZATION = "optimization"


class MigrationPriority(IntEnum):
    """Migration priority levels with numeric ordering"""

    
    EMERGENCY = 1      # Critical system failures, security breaches
    CRITICAL = 2       # Production issues, data corruption
    HIGH = 3          # Important features, performance issues
    MEDIUM = 4        # Standard features, improvements
    LOW = 5           # Nice-to-have, cleanup tasks
    MAINTENANCE = 6   # Routine maintenance, optimizations


class MigrationStatus(Enum):
    """
Comprehensive migration status tracking"""
    
    # Planning phase
    DRAFT = "draft"
    PLANNED = "planned"
    PENDING = "pending"
    SCHEDULED = "scheduled"
    
    # Validation phase
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"
    VALIDATED = "validated"
    
    # Approval phase
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    APPROVED_WITH_WARNINGS = "approved_with_warnings"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    
    # Execution phase
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    
    # Completion phase
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    
    # Rollback phase
    ROLLBACK_PENDING = "rollback_pending"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    ROLLBACK_FAILED = "rollback_failed"
    
    # Special states
    UNKNOWN = "unknown"
    ARCHIVED = "archived"


class ExecutionMode(Enum):
    """Migration execution modes for different environments"""
    
    # Safety modes
    SAFE_ROLLBACK = "safe_rollback"        # With backup and rollback capability
    ZERO_DOWNTIME = "zero_downtime"        # No service interruption
    MAINTENANCE_WINDOW = "maintenance_window"  # During planned downtime
    
    # Speed modes
    FAST_EXECUTION = "fast_execution"      # Optimized for speed
    PARALLEL_EXECUTION = "parallel_execution"  # Multiple operations simultaneously
    BATCH_EXECUTION = "batch_execution"    # Process in batches
    
    # Testing modes
    DRY_RUN = "dry_run"                   # Simulation only
    VALIDATION_ONLY = "validation_only"   # Validate without execution
    TEST_MODE = "test_mode"               # Test environment execution
    
    # Emergency modes
    EMERGENCY = "emergency"               # Emergency execution, minimal checks
    FORCE = "force"                       # Force execution, bypass safeguards
    RECOVERY = "recovery"                 # Recovery mode execution


class RollbackStrategy(Enum):
    """Rollback strategies for different scenarios"""
    
    # Automatic strategies
    AUTO_ROLLBACK = "auto_rollback"               # Automatic on failure
    CONDITIONAL_ROLLBACK = "conditional_rollback"  # Based on conditions
    
    # Manual strategies
    MANUAL_ROLLBACK = "manual_rollback"           # Manual trigger required
    SAFE_ROLLBACK = "safe_rollback"               # With safety checks
    
    # Backup strategies
    BACKUP_RESTORE = "backup_restore"             # Restore from backup
    POINT_IN_TIME = "point_in_time"               # Point-in-time recovery
    
    # Advanced strategies
    PROGRESSIVE_ROLLBACK = "progressive_rollback"  # Step-by-step rollback
    PARTIAL_ROLLBACK = "partial_rollback"         # Rollback specific components
    
    # Emergency strategies
    EMERGENCY_ROLLBACK = "emergency_rollback"     # Fast emergency rollback
    NO_ROLLBACK = "no_rollback"                   # No rollback capability


class ValidationSeverity(Enum):
    """Validation issue severity levels"""

    
    CRITICAL = "critical"     # Blocks execution
    ERROR = "error"          # Major issues
    WARNING = "warning"      # Minor issues
    INFO = "info"           # Informational
    DEBUG = "debug"         # Debug information


class NotificationLevel(Enum):
    """Notification levels for migration events"""

    
    EMERGENCY = "emergency"   # Immediate attention required
    ALERT = "alert"          # Important notifications
    WARNING = "warning"      # Warning notifications
    INFO = "info"           # Informational notifications
    DEBUG = "debug"         # Debug notifications


class EnvironmentType(Enum):
    """Environment types for migration targeting"""

    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"
    SANDBOX = "sandbox"


class DataClassification(Enum):
    """Data classification levels for security and compliance"""

    
    PUBLIC = "public"                    # Public data
    INTERNAL = "internal"                # Internal use only
    CONFIDENTIAL = "confidential"        # Confidential data
    RESTRICTED = "restricted"            # Restricted access
    PERSONALLY_IDENTIFIABLE = "pii"      # Personal data
    FINANCIAL = "financial"              # Financial data
    HEALTHCARE = "healthcare"            # Healthcare data


class ComplianceFramework(Enum):
    """Compliance frameworks for migration validation"""

    
    GDPR = "gdpr"                        # General Data Protection Regulation
    CCPA = "ccpa"                        # California Consumer Privacy Act
    HIPAA = "hipaa"                      # Health Insurance Portability and Accountability Act
    SOX = "sox"                          # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"                  # Payment Card Industry Data Security Standard
    ISO27001 = "iso27001"                # ISO 27001 Information Security
    SOC2 = "soc2"                        # SOC 2 Type II


class PlatformType(Enum):
    """Platform types for content protection and monetization"""
    
    # Social media platforms
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    
    # Music platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    
    # Content platforms
    PATREON = "patreon"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    TWITCH = "twitch"
    DISCORD = "discord"
    
    # E-commerce platforms
    SHOPIFY = "shopify"
    ETSY = "etsy"
    AMAZON = "amazon"
    
    # Generic
    WEBSITE = "website"
    BLOG = "blog"
    PODCAST = "podcast"
    OTHER = "other"


class ContentType(Enum):
    """Content types for fingerprinting and protection"""
    
    # Audio content
    AUDIO_MUSIC = "audio_music"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_SPEECH = "audio_speech"
    AUDIO_SOUND_EFFECT = "audio_sound_effect"
    
    # Video content
    VIDEO_MUSIC = "video_music"
    VIDEO_EDUCATIONAL = "video_educational"
    VIDEO_ENTERTAINMENT = "video_entertainment"
    VIDEO_DOCUMENTARY = "video_documentary"
    VIDEO_LIVE_STREAM = "video_live_stream"
    
    # Image content
    IMAGE_PHOTO = "image_photo"
    IMAGE_ARTWORK = "image_artwork"
    IMAGE_GRAPHIC = "image_graphic"
    IMAGE_MEME = "image_meme"
    
    # Text content
    TEXT_ARTICLE = "text_article"
    TEXT_BLOG_POST = "text_blog_post"
    TEXT_SOCIAL_POST = "text_social_post"
    TEXT_LYRICS = "text_lyrics"
    TEXT_SCRIPT = "text_script"
    
    # Mixed content
    MULTIMEDIA = "multimedia"
    INTERACTIVE = "interactive"
    LIVE_PERFORMANCE = "live_performance"


class MonetizationModel(Enum):
    """Monetization models for creator revenue"""
    
    # Direct monetization
    SUBSCRIPTION = "subscription"
    ONE_TIME_PURCHASE = "one_time_purchase"
    PAY_PER_VIEW = "pay_per_view"
    DONATION = "donation"
    TIP = "tip"
    
    # Platform monetization
    AD_REVENUE = "ad_revenue"
    PLATFORM_REVENUE_SHARE = "platform_revenue_share"
    CREATOR_FUND = "creator_fund"
    BRAND_PARTNERSHIP = "brand_partnership"
    SPONSORSHIP = "sponsorship"
    
    # Licensing
    LICENSING_FEE = "licensing_fee"
    ROYALTY = "royalty"
    SYNC_LICENSING = "sync_licensing"
    
    # Merchandise
    MERCHANDISE = "merchandise"
    AFFILIATE_MARKETING = "affiliate_marketing"
    
    # Services
    CONSULTATION = "consultation"
    COURSE_SALES = "course_sales"
    WORKSHOP = "workshop"


@dataclass
class MigrationConstraints:
    """Migration execution constraints and limitations"""
    
    max_execution_time_minutes: Optional[int] = None
    max_memory_usage_mb: Optional[int] = None
    max_cpu_usage_percent: Optional[int] = None
    max_disk_space_gb: Optional[int] = None
    
    # Timing constraints
    allowed_execution_hours: Optional[List[int]] = None  # Hours of day (0-23)
    allowed_execution_days: Optional[List[int]] = None   # Days of week (0-6)
    blackout_periods: Optional[List[Dict[str, Any]]] = None
    
    # Dependencies
    required_services: Optional[List[str]] = None
    blocked_by_migrations: Optional[List[str]] = None
    must_run_after: Optional[List[str]] = None
    must_run_before: Optional[List[str]] = None
    
    # Safety constraints
    require_backup: bool = True
    require_approval: bool = False
    require_maintenance_window: bool = False
    allow_data_loss: bool = False
    
    # Environment constraints
    allowed_environments: Optional[List[EnvironmentType]] = None
    prohibited_environments: Optional[List[EnvironmentType]] = None
    
    # Compliance constraints
    compliance_frameworks: Optional[List[ComplianceFramework]] = None
    data_classification_level: Optional[DataClassification] = None
    audit_required: bool = False


@dataclass
class MigrationMetadata:
    """
Comprehensive migration metadata"""
    
    # Basic information
    title: str
    description: str
    version: str
    author: str
    created_at: str
    
    # Classification
    migration_type: MigrationType
    priority: MigrationPriority
    category: str
    tags: List[str]
    
    # Dependencies
    dependencies: List[str]
    conflicts: List[str]
    
    # Documentation
    documentation_url: Optional[str] = None
    change_log: Optional[str] = None
    rollback_instructions: Optional[str] = None
    
    # Testing
    test_coverage: Optional[float] = None
    validation_rules: Optional[List[str]] = None
    
    # Approval
    approvers: Optional[List[str]] = None
    reviewers: Optional[List[str]] = None
    
    # Execution
    constraints: Optional[MigrationConstraints] = None
    estimated_duration_minutes: Optional[int] = None
    resource_requirements: Optional[Dict[str, Any]] = None
    
    # Risk assessment
    risk_level: Optional[str] = None
    impact_assessment: Optional[Dict[str, Any]] = None
    
    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = None


# Utility functions for type handling

def get_migration_type_by_category(category: str) -> List[MigrationType]:
    """
Get migration types by category"""
    
    category_mapping = {
        "schema": [
            MigrationType.SCHEMA_CREATION,
            MigrationType.SCHEMA_MODIFICATION,
            MigrationType.SCHEMA_DELETION
        ],
        "data": [
            MigrationType.DATA_MIGRATION,
            MigrationType.DATA_TRANSFORMATION,
            MigrationType.DATA_CLEANUP,
            MigrationType.DATA_ARCHIVAL
        ],
        "security": [
            MigrationType.SECURITY_ENHANCEMENT,
            MigrationType.PERMISSION_UPDATE,
            MigrationType.ENCRYPTION_MIGRATION
        ],
        "performance": [
            MigrationType.INDEX_CREATION,
            MigrationType.INDEX_MODIFICATION,
            MigrationType.PERFORMANCE_OPTIMIZATION
        ],
        "content_protection": [
            MigrationType.FINGERPRINT_SCHEMA,
            MigrationType.PROTECTION_RULES,
            MigrationType.MONITORING_SETUP
        ],
        "monetization": [
            MigrationType.REVENUE_TRACKING,
            MigrationType.PAYMENT_INTEGRATION,
            MigrationType.ANALYTICS_SCHEMA
        ]
    }
    
    return category_mapping.get(category.lower(), [])


def get_priority_weight(priority: MigrationPriority) -> int:
    """Get numeric weight for priority comparison"""
    return priority.value


def is_critical_migration(migration_type: MigrationType, priority: MigrationPriority) -> bool:
    """
Determine if migration is critical"""
    
    critical_types = [
        MigrationType.SECURITY_ENHANCEMENT,
        MigrationType.HOTFIX,
        MigrationType.EMERGENCY_PATCH,
        MigrationType.RECOVERY
    ]
    
    return (
        migration_type in critical_types or
        priority in [MigrationPriority.EMERGENCY, MigrationPriority.CRITICAL]
    )


def requires_maintenance_window(migration_type: MigrationType) -> bool:
    """
Determine if migration requires maintenance window"""
    
    maintenance_types = [
        MigrationType.SCHEMA_DELETION,
        MigrationType.DATA_MIGRATION,
        MigrationType.INFRASTRUCTURE_SETUP,
        MigrationType.MICROSERVICE_DEPLOYMENT
    ]
    
    return migration_type in maintenance_types


def get_default_rollback_strategy(migration_type: MigrationType) -> RollbackStrategy:
    """
Get default rollback strategy for migration type"""
    
    strategy_mapping = {
        MigrationType.SCHEMA_CREATION: RollbackStrategy.SAFE_ROLLBACK,
        MigrationType.SCHEMA_MODIFICATION: RollbackStrategy.BACKUP_RESTORE,
        MigrationType.SCHEMA_DELETION: RollbackStrategy.NO_ROLLBACK,
        MigrationType.DATA_MIGRATION: RollbackStrategy.POINT_IN_TIME,
        MigrationType.SECURITY_ENHANCEMENT: RollbackStrategy.MANUAL_ROLLBACK,
        MigrationType.HOTFIX: RollbackStrategy.AUTO_ROLLBACK,
        MigrationType.EMERGENCY_PATCH: RollbackStrategy.EMERGENCY_ROLLBACK
    }
    
    return strategy_mapping.get(migration_type, RollbackStrategy.SAFE_ROLLBACK)


# Export all types and utilities
__all__ = [
    # Core enums
    "MigrationType",
    "MigrationPriority", 
    "MigrationStatus",
    "ExecutionMode",
    "RollbackStrategy",
    "ValidationSeverity",
    "NotificationLevel",
    "EnvironmentType",
    
    # Security and compliance
    "DataClassification",
    "ComplianceFramework",
    
    # Platform and content
    "PlatformType",
    "ContentType",
    "MonetizationModel",
    
    # Data classes
    "MigrationConstraints",
    "MigrationMetadata",
    
    # Utility functions
    "get_migration_type_by_category",
    "get_priority_weight",
    "is_critical_migration",
    "requires_maintenance_window",
    "get_default_rollback_strategy"
]
