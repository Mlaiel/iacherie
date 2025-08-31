"""
DMCA Configuration Module
========================

Professional DMCA configuration for automated Digital Millennium Copyright Act compliance.
Supports automated notice generation, counter-notifications, and safe harbor compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

  COPYRIGHT WARNING:
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


class DMCANoticeType(str, Enum):
    """Types of DMCA notices."""
    TAKEDOWN = "takedown"
    COUNTER_NOTIFICATION = "counter_notification"
    REPEAT_INFRINGER = "repeat_infringer"
    SAFE_HARBOR = "safe_harbor"
    SUBPOENA = "subpoena"


class DMCAStatus(str, Enum):
    """Status of DMCA processes."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"
    REJECTED = "rejected"
    COUNTER_CLAIMED = "counter_claimed"
    RESTORED = "restored"
    ESCALATED = "escalated"
    COMPLETED = "completed"


class InfringementType(str, Enum):
    """Types of copyright infringement."""
    EXACT_COPY = "exact_copy"
    SUBSTANTIAL_SIMILARITY = "substantial_similarity"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    UNAUTHORIZED_PUBLIC_PERFORMANCE = "unauthorized_public_performance"
    UNAUTHORIZED_DERIVATIVE_WORK = "unauthorized_derivative_work"
    CIRCUMVENTION_OF_PROTECTION = "circumvention_of_protection"


@dataclass
class CopyrightHolderInfo:
    """Copyright holder information."""
    name: str
    address: str
    city: str
    state_province: str
    postal_code: str
    country: str
    email: str
    phone: str
    organization: Optional[str] = None
    title: Optional[str] = None
    authorized_representative: bool = False
    power_of_attorney: bool = False
    registration_number: Optional[str] = None


@dataclass
class InfringementEvidence:
    """Evidence of copyright infringement."""
    original_work_url: str
    infringing_work_url: str
    similarity_score: float
    evidence_screenshots: List[str] = field(default_factory=list)
    evidence_videos: List[str] = field(default_factory=list)
    fingerprint_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata_comparison: Dict[str, Any] = field(default_factory=dict)
    timestamp_evidence: Dict[str, datetime] = field(default_factory=dict)
    witness_statements: List[str] = field(default_factory=list)
    expert_analysis: Optional[str] = None
    technical_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DMCANoticeTemplate:
    """Template for DMCA notices."""
    template_id: str
    notice_type: DMCANoticeType
    subject_template: str
    body_template: str
    required_fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    attachments_required: List[str] = field(default_factory=list)
    legal_reviewed: bool = False
    jurisdiction: str = "US"
    language: str = "en"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SafeHarborConfig:
    """Safe Harbor compliance configuration."""
    enable_safe_harbor: bool = True
    designated_agent_name: str = ""
    designated_agent_address: str = ""
    designated_agent_email: str = ""
    designated_agent_phone: str = ""
    copyright_office_registration: bool = False
    registration_number: Optional[str] = None
    takedown_response_time_hours: int = 24
    counter_notification_response_time_days: int = 14
    repeat_infringer_policy: bool = True
    repeat_infringer_threshold: int = 3
    repeat_infringer_timeframe_months: int = 12
    terminate_repeat_infringers: bool = True
    accommodation_standard_measures: bool = True


@dataclass
class CounterNotificationConfig:
    """Counter-notification handling configuration."""
    enable_counter_notifications: bool = True
    auto_process_counter_notifications: bool = False
    legal_review_required: bool = True
    good_faith_review_enabled: bool = True
    perjury_penalty_warning: bool = True
    restoration_period_days: int = 14
    counter_notification_fee: Optional[float] = None
    require_sworn_statement: bool = True
    require_consent_to_jurisdiction: bool = True
    identity_verification_required: bool = True
    supporting_evidence_required: bool = True


@dataclass
class AutomationConfig:
    """Automation configuration for DMCA processes."""
    enable_automated_detection: bool = True
    enable_automated_notice_generation: bool = True
    enable_automated_submission: bool = False
    manual_review_threshold: float = 0.95
    batch_processing_enabled: bool = True
    batch_size: int = 25
    processing_schedule: str = "hourly"  # hourly, daily, weekly
    confidence_threshold: float = 0.9
    false_positive_prevention: bool = True
    duplicate_detection: bool = True
    rate_limiting_enabled: bool = True
    max_notices_per_day: int = 100
    cooling_off_period_hours: int = 24


@dataclass
class TrackingConfig:
    """Tracking and reporting configuration."""
    enable_tracking: bool = True
    track_submission_status: bool = True
    track_response_times: bool = True
    track_success_rates: bool = True
    enable_analytics: bool = True
    generate_reports: bool = True
    reporting_frequency: str = "weekly"
    dashboard_metrics_enabled: bool = True
    export_data_enabled: bool = True
    audit_trail_enabled: bool = True
    retention_period_years: int = 7
    compliance_monitoring: bool = True


class DMCAConfig:
    """
    Professional DMCA configuration manager.
    Provides industrial-grade configuration for DMCA compliance and automation.
    """
    
    def __init__(self):
        # General DMCA settings
        self.enable_dmca_system: bool = True
        self.jurisdiction: str = "US"
        self.service_provider_name: str = ""
        self.service_provider_type: str = "online_service_provider"
        self.dmca_agent_registered: bool = False
        
        # Configuration components
        self.safe_harbor = SafeHarborConfig()
        self.counter_notification = CounterNotificationConfig()
        self.automation = AutomationConfig()
        self.tracking = TrackingConfig()
        
        # Copyright holder information
        self.copyright_holder: Optional[CopyrightHolderInfo] = None
        
        # Notice templates
        self.notice_templates: Dict[str, DMCANoticeTemplate] = {}
        
        # Platform-specific configurations
        self.platform_configs: Dict[str, Dict[str, Any]] = {}
        
        # Legal and compliance settings
        self.legal_counsel_contact: str = ""
        self.legal_entity_name: str = ""
        self.require_legal_review: bool = True
        self.digital_signature_required: bool = True
        
        # Performance settings
        self.max_concurrent_processes: int = 50
        self.processing_timeout_minutes: int = 30
        self.queue_priority_enabled: bool = True
        
        # Initialize default configurations
        self._initialize_notice_templates()
        self._initialize_platform_configs()
        
        # Load environment configurations
        self._load_from_environment()
    
    def _initialize_notice_templates(self) -> None:
        """Initialize default DMCA notice templates."""
        # Standard takedown notice template
        takedown_template = DMCANoticeTemplate(
            template_id="standard_takedown",
            notice_type=DMCANoticeType.TAKEDOWN,
            subject_template="DMCA Takedown Notice - Copyright Infringement",
            body_template="""
To Whom It May Concern:

This is a notification of copyright infringement pursuant to the Digital Millennium Copyright Act (17 U.S.C. § 512).

1. IDENTIFICATION OF COPYRIGHTED WORK:
The copyrighted work claimed to have been infringed is:
{copyrighted_work_description}
{original_work_url}

2. IDENTIFICATION OF INFRINGING MATERIAL:
The infringing material to be removed or access disabled is located at:
{infringing_material_urls}

3. CONTACT INFORMATION:
{copyright_holder_name}
{copyright_holder_address}
{copyright_holder_phone}
{copyright_holder_email}

4. GOOD FAITH BELIEF:
I have a good faith belief that use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law.

5. ACCURACY AND AUTHORITY:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner, or am authorized to act on behalf of the owner, of an exclusive right that is allegedly infringed.

6. ELECTRONIC SIGNATURE:
{electronic_signature}

Date: {notice_date}

{copyright_holder_name}
{copyright_holder_title}
            """,
            required_fields=[
                "copyrighted_work_description", "original_work_url",
                "infringing_material_urls", "copyright_holder_name",
                "copyright_holder_address", "copyright_holder_phone",
                "copyright_holder_email", "electronic_signature", "notice_date"
            ],
            attachments_required=["evidence_package"],
            legal_reviewed=True
        )
        
        # Counter-notification template
        counter_template = DMCANoticeTemplate(
            template_id="counter_notification",
            notice_type=DMCANoticeType.COUNTER_NOTIFICATION,
            subject_template="DMCA Counter-Notification",
            body_template="""
To Whom It May Concern:

This is a counter-notification pursuant to the Digital Millennium Copyright Act (17 U.S.C. § 512(g)(3)).

1. IDENTIFICATION OF REMOVED MATERIAL:
The material that was removed or disabled is:
{removed_material_description}
{removed_material_urls}

2. SUBSCRIBER INFORMATION:
{subscriber_name}
{subscriber_address}
{subscriber_phone}
{subscriber_email}

3. GOOD FAITH BELIEF:
I swear, under penalty of perjury, that I have a good faith belief that the material was removed or disabled as a result of mistake or misidentification.

4. CONSENT TO JURISDICTION:
I consent to the jurisdiction of Federal District Court for the judicial district in which my address is located, or if my address is outside of the United States, for any judicial district in which the service provider may be found, and I will accept service of process from the person who provided the original DMCA notification or an agent of such person.

5. ELECTRONIC SIGNATURE:
{electronic_signature}

Date: {counter_notification_date}

{subscriber_name}
            """,
            required_fields=[
                "removed_material_description", "removed_material_urls",
                "subscriber_name", "subscriber_address", "subscriber_phone",
                "subscriber_email", "electronic_signature", "counter_notification_date"
            ]
        )
        
        self.notice_templates["standard_takedown"] = takedown_template
        self.notice_templates["counter_notification"] = counter_template
    
    def _initialize_platform_configs(self) -> None:
        """Initialize platform-specific DMCA configurations."""
        self.platform_configs = {
            "youtube": {
                "submission_url": "https://www.youtube.com/copyright_complaint_form",
                "api_endpoint": None,
                "requires_web_form": True,
                "processing_time_hours": 24,
                "supports_counter_notifications": True,
                "automated_submission": False
            },
            "facebook": {
                "submission_url": "https://www.facebook.com/legal/copyright.php",
                "api_endpoint": None,
                "requires_web_form": True,
                "processing_time_hours": 48,
                "supports_counter_notifications": True,
                "automated_submission": False
            },
            "instagram": {
                "submission_url": "https://help.instagram.com/contact/372592039493026",
                "api_endpoint": None,
                "requires_web_form": True,
                "processing_time_hours": 48,
                "supports_counter_notifications": True,
                "automated_submission": False
            },
            "twitter": {
                "submission_url": "https://help.twitter.com/forms/dmca",
                "api_endpoint": None,
                "requires_web_form": True,
                "processing_time_hours": 24,
                "supports_counter_notifications": True,
                "automated_submission": False
            }
        }
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        self.enable_dmca_system = os.getenv("DMCA_ENABLED", "true").lower() == "true"
        self.jurisdiction = os.getenv("DMCA_JURISDICTION", "US")
        self.service_provider_name = os.getenv("DMCA_SERVICE_PROVIDER_NAME", "")
        self.dmca_agent_registered = os.getenv("DMCA_AGENT_REGISTERED", "false").lower() == "true"
        
        # Performance settings
        self.max_concurrent_processes = int(os.getenv("DMCA_MAX_CONCURRENT", "50"))
        self.processing_timeout_minutes = int(os.getenv("DMCA_TIMEOUT_MINUTES", "30"))
        
        # Safe harbor settings
        self.safe_harbor.designated_agent_name = os.getenv("DMCA_AGENT_NAME", "")
        self.safe_harbor.designated_agent_email = os.getenv("DMCA_AGENT_EMAIL", "")
        self.safe_harbor.designated_agent_address = os.getenv("DMCA_AGENT_ADDRESS", "")
        self.safe_harbor.takedown_response_time_hours = int(os.getenv("DMCA_RESPONSE_TIME_HOURS", "24"))
        
        # Automation settings
        self.automation.enable_automated_detection = os.getenv("DMCA_AUTO_DETECTION", "true").lower() == "true"
        self.automation.enable_automated_submission = os.getenv("DMCA_AUTO_SUBMISSION", "false").lower() == "true"
        self.automation.confidence_threshold = float(os.getenv("DMCA_CONFIDENCE_THRESHOLD", "0.9"))
        self.automation.max_notices_per_day = int(os.getenv("DMCA_MAX_NOTICES_PER_DAY", "100"))
        
        # Legal settings
        self.legal_counsel_contact = os.getenv("DMCA_LEGAL_COUNSEL", "")
        self.require_legal_review = os.getenv("DMCA_LEGAL_REVIEW_REQUIRED", "true").lower() == "true"
    
    def set_copyright_holder(self, holder_info: CopyrightHolderInfo) -> None:
        """Set copyright holder information."""
        self.copyright_holder = holder_info
    
    def get_notice_template(self, template_id: str) -> DMCANoticeTemplate:
        """Get DMCA notice template by ID."""
        if template_id not in self.notice_templates:
            raise ValueError(f"Notice template not found: {template_id}")
        return self.notice_templates[template_id]
    
    def add_notice_template(self, template: DMCANoticeTemplate) -> None:
        """Add custom DMCA notice template."""
        self.notice_templates[template.template_id] = template
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific DMCA configuration."""
        if platform not in self.platform_configs:
            raise ValueError(f"Platform configuration not found: {platform}")
        return self.platform_configs[platform]
    
    def should_auto_submit(self, confidence_score: float, infringement_value: float = 0.0) -> bool:
        """Determine if DMCA notice should be automatically submitted."""
        if not self.automation.enable_automated_submission:
            return False
        
        if confidence_score < self.automation.confidence_threshold:
            return False
        
        if confidence_score < self.automation.manual_review_threshold:
            return False
        
        # High-value infringement might require manual review
        if infringement_value > 10000.0 and self.require_legal_review:
            return False
        
        return True
    
    def is_repeat_infringer(self, user_id: str, infringement_history: List[datetime]) -> bool:
        """Check if user is a repeat infringer based on history."""
        if not self.safe_harbor.repeat_infringer_policy:
            return False
        
        threshold_date = datetime.now() - timedelta(
            days=self.safe_harbor.repeat_infringer_timeframe_months * 30
        )
        
        recent_infringements = [
            date for date in infringement_history if date >= threshold_date
        ]
        
        return len(recent_infringements) >= self.safe_harbor.repeat_infringer_threshold
    
    def should_terminate_user(self, user_id: str, infringement_history: List[datetime]) -> bool:
        """Determine if repeat infringer should be terminated."""
        if not self.safe_harbor.terminate_repeat_infringers:
            return False
        
        return self.is_repeat_infringer(user_id, infringement_history)
    
    def generate_notice_content(self, template_id: str, **variables) -> str:
        """Generate DMCA notice content from template."""
        template = self.get_notice_template(template_id)
        
        # Check required fields
        missing_fields = []
        for field in template.required_fields:
            if field not in variables:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Generate content
        content = template.body_template.format(**variables)
        return content
    
    def validate_notice_requirements(self, notice_type: DMCANoticeType,
                                   evidence: InfringementEvidence) -> List[str]:
        """Validate DMCA notice requirements."""
        issues = []
        
        # General requirements
        if not evidence.original_work_url:
            issues.append("Original work URL is required")
        
        if not evidence.infringing_work_url:
            issues.append("Infringing work URL is required")
        
        if evidence.similarity_score < 0.7:
            issues.append("Similarity score too low for strong infringement claim")
        
        # Evidence requirements
        if not evidence.evidence_screenshots:
            issues.append("Screenshot evidence is recommended")
        
        if not evidence.fingerprint_analysis:
            issues.append("Technical analysis is recommended")
        
        # Copyright holder requirements
        if not self.copyright_holder:
            issues.append("Copyright holder information is required")
        elif not all([
            self.copyright_holder.name,
            self.copyright_holder.email,
            self.copyright_holder.address
        ]):
            issues.append("Complete copyright holder information is required")
        
        # Takedown-specific requirements
        if notice_type == DMCANoticeType.TAKEDOWN:
            if evidence.similarity_score < self.automation.confidence_threshold:
                issues.append(f"Similarity score should be >= {self.automation.confidence_threshold}")
        
        return issues
    
    def calculate_processing_priority(self, infringement_type: InfringementType,
                                    similarity_score: float,
                                    commercial_impact: float) -> int:
        """Calculate processing priority (1-5, 5 being highest priority)."""
        priority = 1
        
        # Infringement type priority
        type_priorities = {
            InfringementType.EXACT_COPY: 5,
            InfringementType.SUBSTANTIAL_SIMILARITY: 4,
            InfringementType.UNAUTHORIZED_DISTRIBUTION: 4,
            InfringementType.UNAUTHORIZED_PUBLIC_PERFORMANCE: 3,
            InfringementType.UNAUTHORIZED_DERIVATIVE_WORK: 3,
            InfringementType.CIRCUMVENTION_OF_PROTECTION: 5
        }
        priority = max(priority, type_priorities.get(infringement_type, 1))
        
        # Similarity score adjustment
        if similarity_score >= 0.95:
            priority = min(priority + 2, 5)
        elif similarity_score >= 0.85:
            priority = min(priority + 1, 5)
        
        # Commercial impact adjustment
        if commercial_impact > 10000:
            priority = 5
        elif commercial_impact > 1000:
            priority = min(priority + 1, 5)
        
        return priority
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        # General validation
        if self.enable_dmca_system and not self.service_provider_name:
            issues.append("Service provider name is required when DMCA system is enabled")
        
        if self.max_concurrent_processes <= 0:
            issues.append("Max concurrent processes must be positive")
        
        # Safe harbor validation
        if self.safe_harbor.enable_safe_harbor:
            if not self.safe_harbor.designated_agent_name:
                issues.append("Designated agent name is required for Safe Harbor")
            
            if not self.safe_harbor.designated_agent_email:
                issues.append("Designated agent email is required for Safe Harbor")
            
            if self.safe_harbor.takedown_response_time_hours <= 0:
                issues.append("Takedown response time must be positive")
        
        # Automation validation
        if not 0.0 <= self.automation.confidence_threshold <= 1.0:
            issues.append("Confidence threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.automation.manual_review_threshold <= 1.0:
            issues.append("Manual review threshold must be between 0.0 and 1.0")
        
        if self.automation.max_notices_per_day <= 0:
            issues.append("Max notices per day must be positive")
        
        # Copyright holder validation
        if not self.copyright_holder:
            issues.append("Copyright holder information is required")
        
        # Legal validation
        if self.require_legal_review and not self.legal_counsel_contact:
            issues.append("Legal counsel contact is required when legal review is enabled")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""



        return {
            "enable_dmca_system": self.enable_dmca_system,
            "jurisdiction": self.jurisdiction,
            "service_provider_name": self.service_provider_name,
            "service_provider_type": self.service_provider_type,
            "dmca_agent_registered": self.dmca_agent_registered,
            "legal_counsel_contact": self.legal_counsel_contact,
            "legal_entity_name": self.legal_entity_name,
            "require_legal_review": self.require_legal_review,
            "digital_signature_required": self.digital_signature_required,
            "max_concurrent_processes": self.max_concurrent_processes,
            "processing_timeout_minutes": self.processing_timeout_minutes,
            "queue_priority_enabled": self.queue_priority_enabled,
            "safe_harbor": self.safe_harbor.__dict__,
            "counter_notification": self.counter_notification.__dict__,
            "automation": self.automation.__dict__,
            "tracking": self.tracking.__dict__,
            "copyright_holder": self.copyright_holder.__dict__ if self.copyright_holder else None,
            "notice_templates": {k: v.__dict__ for k, v in self.notice_templates.items()},
            "platform_configs": self.platform_configs
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DMCAConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        # Load basic settings
        basic_fields = [
            "enable_dmca_system", "jurisdiction", "service_provider_name",
            "service_provider_type", "dmca_agent_registered", "legal_counsel_contact",
            "legal_entity_name", "require_legal_review", "digital_signature_required",
            "max_concurrent_processes", "processing_timeout_minutes", "queue_priority_enabled"
        ]
        
        for field in basic_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        # Load component configurations
        component_map = {
            "safe_harbor": config.safe_harbor,
            "counter_notification": config.counter_notification,
            "automation": config.automation,
            "tracking": config.tracking
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        # Load copyright holder
        if "copyright_holder" in config_dict and config_dict["copyright_holder"]:
            holder_data = config_dict["copyright_holder"]
            config.copyright_holder = CopyrightHolderInfo(**holder_data)
        
        # Load templates
        if "notice_templates" in config_dict:
            config.notice_templates = {}
            for template_id, template_data in config_dict["notice_templates"].items():
                template = DMCANoticeTemplate(**template_data)
                config.notice_templates[template_id] = template
        
        # Load platform configs
        if "platform_configs" in config_dict:
            config.platform_configs = config_dict["platform_configs"]
        
        return config
