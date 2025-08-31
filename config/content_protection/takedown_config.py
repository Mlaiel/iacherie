"""Takedown Configuration Module
============================

Professional takedown configuration for automated content removal and legal compliance.
Supports DMCA notices, platform-specific takedown procedures, and legal tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
from datetime import datetime, timedelta


class TakedownType(str, Enum):
    """Types of takedown procedures."""
    DMCA = "dmca"
    EU_COPYRIGHT = "eu_copyright"
    PLATFORM_SPECIFIC = "platform_specific"
    CEASE_DESIST = "cease_desist"
    COURT_ORDER = "court_order"
    VOLUNTARY = "voluntary"


class TakedownStatus(str, Enum):
    """Status of takedown requests."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    COUNTER_CLAIMED = "counter_claimed"
    APPEALED = "appealed"


class PlatformType(str, Enum):
    """Supported platforms for takedown procedures."""
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"


class LegalJurisdiction(str, Enum):
    """Legal jurisdictions for takedown procedures."""
    US = "us"
    EU = "eu"
    UK = "uk"
    GERMANY = "germany"
    FRANCE = "france"
    CANADA = "canada"
    AUSTRALIA = "australia"
    JAPAN = "japan"
    INTERNATIONAL = "international"


@dataclass
class TakedownTemplate:
    """Template for takedown notices."""
    template_id: str
    template_name: str
    takedown_type: TakedownType
    platform: PlatformType
    jurisdiction: LegalJurisdiction
    subject_line: str
    body_template: str
    required_fields: List[str]
    attachments_required: List[str]
    language: str = "en"
    legal_reviewed: bool = False
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DMCAConfig:
    """DMCA takedown configuration."""
    enable_dmca: bool = True
    copyright_holder_name: str = ""
    copyright_holder_address: str = ""
    copyright_holder_email: str = ""
    copyright_holder_phone: str = ""
    authorized_agent_name: str = ""
    authorized_agent_email: str = ""
    digital_signature_enabled: bool = True
    good_faith_belief_statement: str = "I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law."
    accuracy_statement: str = "I swear, under penalty of perjury, that the information in the notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner."
    auto_submit_enabled: bool = False
    manual_review_required: bool = True
    include_evidence: bool = True
    evidence_types: List[str] = field(default_factory=lambda: [
        "original_work", "infringing_content", "similarity_report", "timestamp_evidence"
    ])


@dataclass
class PlatformTakedownConfig:
    """Platform-specific takedown configuration."""
    platform: PlatformType
    enabled: bool = True
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    submission_method: str = "api"  # api, web_form, email
    rate_limit_requests_per_day: int = 100
    rate_limit_requests_per_hour: int = 10
    processing_time_hours: int = 24
    follow_up_interval_days: int = 7
    max_follow_ups: int = 3
    auto_escalation: bool = True
    escalation_days: int = 14
    success_indicators: List[str] = field(default_factory=lambda: [
        "content_removed", "access_blocked", "user_notified"
    ])
    platform_specific_fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class LegalComplianceConfig:
    """Legal compliance configuration."""
    primary_jurisdiction: LegalJurisdiction = LegalJurisdiction.EU
    secondary_jurisdictions: List[LegalJurisdiction] = field(default_factory=list)
    legal_counsel_contact: str = ""
    legal_entity_name: str = ""
    legal_entity_address: str = ""
    legal_entity_registration: str = ""
    enable_legal_review: bool = True
    legal_review_threshold: str = "high_value"  # all, high_value, complex_cases
    document_retention_years: int = 7
    compliance_monitoring: bool = True
    audit_trail_enabled: bool = True
    notification_requirements: List[str] = field(default_factory=lambda: [
        "copyright_holder", "alleged_infringer", "platform_operator"
    ])


@dataclass
class EscalationConfig:
    """Escalation configuration for failed takedowns."""
    enable_escalation: bool = True
    auto_escalation: bool = True
    escalation_levels: List[str] = field(default_factory=lambda: [
        "platform_resubmission", "legal_letter", "court_filing"
    ])
    escalation_triggers: List[str] = field(default_factory=lambda: [
        "rejection", "no_response", "partial_compliance", "repeated_infringement"
    ])
    escalation_delays: Dict[str, int] = field(default_factory=lambda: {
        "platform_resubmission": 3,  # days
        "legal_letter": 7,
        "court_filing": 14
    })
    legal_action_threshold: float = 10000.0  # monetary value
    cease_desist_enabled: bool = True
    court_filing_enabled: bool = False
    require_legal_approval: bool = True


@dataclass
class NotificationConfig:
    """Notification configuration for takedown processes."""
    enable_notifications: bool = True
    email_notifications: bool = True
    webhook_notifications: bool = True
    dashboard_notifications: bool = True
    sms_notifications: bool = False
    notification_events: List[str] = field(default_factory=lambda: [
        "submission_sent", "acknowledgment_received", "status_updated",
        "completion", "rejection", "escalation_triggered"
    ])
    notification_recipients: List[str] = field(default_factory=list)
    notification_cooldown_minutes: int = 30
    batch_notifications: bool = True
    batch_interval_hours: int = 4


@dataclass
class DocumentationConfig:
    """Documentation and evidence configuration."""
    enable_documentation: bool = True
    screenshot_evidence: bool = True
    video_evidence: bool = True
    metadata_collection: bool = True
    chain_of_custody: bool = True
    timestamping: bool = True
    digital_signatures: bool = True
    evidence_encryption: bool = True
    backup_evidence: bool = True
    evidence_retention_years: int = 7
    evidence_formats: List[str] = field(default_factory=lambda: [
        "pdf", "png", "mp4", "json", "xml"
    ])
    quality_requirements: Dict[str, Any] = field(default_factory=lambda: {
        "screenshot_dpi": 150,
        "video_quality": "720p",
        "compression": "lossless"
    })


class TakedownConfig:
    """
    Professional takedown configuration manager.
    Provides industrial-grade configuration for automated content takedown procedures.
    """
    
    def __init__(self):
        # General takedown settings
        self.enable_takedown_system: bool = True
        self.default_takedown_type: TakedownType = TakedownType.DMCA
        self.auto_takedown_enabled: bool = False
        self.manual_approval_required: bool = True
        self.confidence_threshold: float = 0.95
        
        # Core configurations
        self.dmca = DMCAConfig()
        self.legal_compliance = LegalComplianceConfig()
        self.escalation = EscalationConfig()
        self.notifications = NotificationConfig()
        self.documentation = DocumentationConfig()
        
        # Platform configurations
        self.platforms: Dict[PlatformType, PlatformTakedownConfig] = {}
        self._initialize_platform_configs()
        
        # Templates
        self.templates: Dict[str, TakedownTemplate] = {}
        self._initialize_templates()
        
        # Performance settings
        self.max_concurrent_takedowns: int = 50
        self.processing_timeout_minutes: int = 60
        self.batch_processing: bool = True
        self.batch_size: int = 20
        
        # Load environment configurations
        self._load_from_environment()
    
    def _initialize_platform_configs(self) -> None:
        """Initialize default platform configurations."""
        platform_defaults = {
            PlatformType.YOUTUBE: {
                "processing_time_hours": 24,
                "rate_limit_requests_per_day": 100,
                "submission_method": "web_form"
            },
            PlatformType.FACEBOOK: {
                "processing_time_hours": 48,
                "rate_limit_requests_per_day": 50,
                "submission_method": "web_form"
            },
            PlatformType.INSTAGRAM: {
                "processing_time_hours": 48,
                "rate_limit_requests_per_day": 50,
                "submission_method": "web_form"
            },
            PlatformType.TIKTOK: {
                "processing_time_hours": 72,
                "rate_limit_requests_per_day": 30,
                "submission_method": "web_form"
            },
            PlatformType.TWITTER: {
                "processing_time_hours": 24,
                "rate_limit_requests_per_day": 75,
                "submission_method": "web_form"
            },
            PlatformType.SPOTIFY: {
                "processing_time_hours": 24,
                "rate_limit_requests_per_day": 25,
                "submission_method": "email"
            },
            PlatformType.SOUNDCLOUD: {
                "processing_time_hours": 48,
                "rate_limit_requests_per_day": 20,
                "submission_method": "web_form"
            }
        }
        
        for platform, defaults in platform_defaults.items():
            config = PlatformTakedownConfig(platform=platform)
            for key, value in defaults.items():
                setattr(config, key, value)
            self.platforms[platform] = config
    
    def _initialize_templates(self) -> None:
        """Initialize default takedown templates."""
        # DMCA template
        dmca_template = TakedownTemplate(
            template_id="dmca_standard",
            template_name="Standard DMCA Takedown Notice",
            takedown_type=TakedownType.DMCA,
            platform=PlatformType.GENERIC_WEB,
            jurisdiction=LegalJurisdiction.US,
            subject_line="DMCA Takedown Notice - Copyright Infringement",
            body_template="""To Whom It May Concern:

I am writing to notify you of copyright infringement occurring on your platform.

1. IDENTIFICATION OF COPYRIGHTED WORK:
{original_work_description}

2. IDENTIFICATION OF INFRINGING MATERIAL:
{infringing_content_urls}

3. CONTACT INFORMATION:
{copyright_holder_info}

4. GOOD FAITH BELIEF STATEMENT:
{good_faith_statement}

5. ACCURACY STATEMENT:
{accuracy_statement}

Please remove or disable access to the infringing material immediately.

Sincerely,
{copyright_holder_name}
{digital_signature}
            """,
            required_fields=[
                "original_work_description", "infringing_content_urls",
                "copyright_holder_info", "copyright_holder_name"
            ],
            attachments_required=["evidence_package", "copyright_proof"]
        )
        
        self.templates["dmca_standard"] = dmca_template
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        self.enable_takedown_system = os.getenv("TAKEDOWN_ENABLED", "true").lower() == "true"
        self.auto_takedown_enabled = os.getenv("TAKEDOWN_AUTO_ENABLED", "false").lower() == "true"
        self.manual_approval_required = os.getenv("TAKEDOWN_MANUAL_APPROVAL", "true").lower() == "true"
        self.confidence_threshold = float(os.getenv("TAKEDOWN_CONFIDENCE_THRESHOLD", "0.95"))
        
        # Performance settings
        self.max_concurrent_takedowns = int(os.getenv("TAKEDOWN_MAX_CONCURRENT", "50"))
        self.processing_timeout_minutes = int(os.getenv("TAKEDOWN_TIMEOUT_MINUTES", "60"))
        self.batch_size = int(os.getenv("TAKEDOWN_BATCH_SIZE", "20"))
        
        # DMCA settings
        self.dmca.copyright_holder_name = os.getenv("DMCA_COPYRIGHT_HOLDER_NAME", "")
        self.dmca.copyright_holder_email = os.getenv("DMCA_COPYRIGHT_HOLDER_EMAIL", "")
        self.dmca.authorized_agent_email = os.getenv("DMCA_AUTHORIZED_AGENT_EMAIL", "")
        
        # Legal settings
        jurisdiction = os.getenv("TAKEDOWN_PRIMARY_JURISDICTION", "eu")
        self.legal_compliance.primary_jurisdiction = LegalJurisdiction(jurisdiction)
        self.legal_compliance.legal_counsel_contact = os.getenv("TAKEDOWN_LEGAL_COUNSEL", "")
        
        # Load platform credentials
        for platform in self.platforms:
            platform_prefix = f"TAKEDOWN_{platform.upper()}_"
            platform_config = self.platforms[platform]
            platform_config.api_key = os.getenv(f"{platform_prefix}API_KEY")
            platform_config.api_secret = os.getenv(f"{platform_prefix}API_SECRET")
            platform_config.api_endpoint = os.getenv(f"{platform_prefix}API_ENDPOINT")
    
    def get_platform_config(self, platform: PlatformType) -> PlatformTakedownConfig:
        """Get configuration for specific platform."""
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        return self.platforms[platform]
    
    def get_template(self, template_id: str) -> TakedownTemplate:
        """Get takedown template by ID."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        return self.templates[template_id]
    
    def add_template(self, template: TakedownTemplate) -> None:
        """Add custom takedown template."""
        self.templates[template.template_id] = template
    
    def enable_platform(self, platform: PlatformType) -> None:
        """Enable takedown for specific platform."""
        if platform in self.platforms:
            self.platforms[platform].enabled = True
        else:
            config = PlatformTakedownConfig(platform=platform, enabled=True)
            self.platforms[platform] = config
    
    def disable_platform(self, platform: PlatformType) -> None:
        """Disable takedown for specific platform."""
        if platform in self.platforms:
            self.platforms[platform].enabled = False
    
    def get_enabled_platforms(self) -> List[PlatformType]:
        """Get list of enabled platforms."""
        return [platform for platform, config in self.platforms.items() if config.enabled]
    
    def should_auto_takedown(self, similarity_score: float, content_value: float = 0.0) -> bool:
        """Determine if content should be automatically taken down."""
        if not self.auto_takedown_enabled:
            return False
        
        if similarity_score < self.confidence_threshold:
            return False
        
        # Consider escalation threshold for high-value content
        if content_value >= self.escalation.legal_action_threshold:
            return False  # Require manual review for high-value cases
        
        return True
    
    def should_escalate(self, status: TakedownStatus, days_elapsed: int, 
                       rejection_count: int = 0) -> bool:
        """Determine if takedown should be escalated."""
        if not self.escalation.enable_escalation:
            return False
        
        if status == TakedownStatus.REJECTED and rejection_count >= 1:
            return True
        
        if status == TakedownStatus.SUBMITTED and days_elapsed >= self.escalation.escalation_delays.get("platform_resubmission", 3):
            return True
        
        if status == TakedownStatus.UNDER_REVIEW and days_elapsed >= 14:
            return True
        
        return False
    
    def get_next_escalation_level(self, current_level: str) -> Optional[str]:
        """Get next escalation level."""
        levels = self.escalation.escalation_levels
        try:
            current_index = levels.index(current_level)
            if current_index + 1 < len(levels):
                return levels[current_index + 1]
        except ValueError:
            pass
        return None
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # Validate general settings
        if not 0.0 <= self.confidence_threshold <= 1.0:
            issues.append("Confidence threshold must be between 0.0 and 1.0")
        
        if self.max_concurrent_takedowns <= 0:
            issues.append("Max concurrent takedowns must be positive")
        
        if self.processing_timeout_minutes <= 0:
            issues.append("Processing timeout must be positive")
        
        # Validate DMCA configuration
        if self.dmca.enable_dmca:
            if not self.dmca.copyright_holder_name:
                issues.append("DMCA copyright holder name is required")
            
            if not self.dmca.copyright_holder_email:
                issues.append("DMCA copyright holder email is required")
        
        # Validate platform configurations
        enabled_platforms = self.get_enabled_platforms()
        if not enabled_platforms:
            issues.append("At least one platform must be enabled")
        
        for platform, config in self.platforms.items():
            if config.enabled:
                if config.submission_method == "api" and not config.api_endpoint:
                    issues.append(f"API endpoint required for {platform} but not configured")
                
                if config.rate_limit_requests_per_day <= 0:
                    issues.append(f"Rate limit for {platform} must be positive")
        
        # Validate legal compliance
        if self.legal_compliance.enable_legal_review and not self.legal_compliance.legal_counsel_contact:
            issues.append("Legal counsel contact required when legal review is enabled")
        
        # Validate escalation settings
        if self.escalation.enable_escalation:
            if self.escalation.legal_action_threshold <= 0:
                issues.append("Legal action threshold must be positive")
            
            if not self.escalation.escalation_levels:
                issues.append("At least one escalation level must be configured")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enable_takedown_system": self.enable_takedown_system,
            "default_takedown_type": self.default_takedown_type,
            "auto_takedown_enabled": self.auto_takedown_enabled,
            "manual_approval_required": self.manual_approval_required,
            "confidence_threshold": self.confidence_threshold,
            "max_concurrent_takedowns": self.max_concurrent_takedowns,
            "processing_timeout_minutes": self.processing_timeout_minutes,
            "batch_processing": self.batch_processing,
            "batch_size": self.batch_size,
            "dmca": self.dmca.__dict__,
            "legal_compliance": self.legal_compliance.__dict__,
            "escalation": self.escalation.__dict__,
            "notifications": self.notifications.__dict__,
            "documentation": self.documentation.__dict__,
            "platforms": {k.value: v.__dict__ for k, v in self.platforms.items()},
            "templates": {k: v.__dict__ for k, v in self.templates.items()}
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TakedownConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Load basic settings
        basic_fields = [
            "enable_takedown_system", "auto_takedown_enabled",
            "manual_approval_required", "confidence_threshold",
            "max_concurrent_takedowns", "processing_timeout_minutes",
            "batch_processing", "batch_size"
        ]
        
        for field in basic_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        if "default_takedown_type" in config_dict:
            config.default_takedown_type = TakedownType(config_dict["default_takedown_type"])
        
        # Load component configurations
        component_map = {
            "dmca": config.dmca,
            "legal_compliance": config.legal_compliance,
            "escalation": config.escalation,
            "notifications": config.notifications,
            "documentation": config.documentation
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        # Load platform configurations
        if "platforms" in config_dict:
            config.platforms = {}
            for platform_str, platform_dict in config_dict["platforms"].items():
                platform = PlatformType(platform_str)
                platform_config = PlatformTakedownConfig(platform=platform)
                for attr_key, attr_value in platform_dict.items():
                    setattr(platform_config, attr_key, attr_value)
                config.platforms[platform] = platform_config
        
        # Load templates
        if "templates" in config_dict:
            config.templates = {}
            for template_id, template_dict in config_dict["templates"].items():
                template = TakedownTemplate(
                    template_id=template_dict["template_id"],
                    template_name=template_dict["template_name"],
                    takedown_type=TakedownType(template_dict["takedown_type"]),
                    platform=PlatformType(template_dict["platform"]),
                    jurisdiction=LegalJurisdiction(template_dict["jurisdiction"]),
                    subject_line=template_dict["subject_line"],
                    body_template=template_dict["body_template"],
                    required_fields=template_dict["required_fields"],
                    attachments_required=template_dict["attachments_required"]
                )
                config.templates[template_id] = template
        
        return config
