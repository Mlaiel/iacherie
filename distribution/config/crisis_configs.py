"""
Crisis Management Configuration for Ainflue Distribution
Provides comprehensive configuration for crisis detection and response

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class CrisisType(str, Enum):
    """Types of crises that can be detected"""
    REPUTATION_DAMAGE = "reputation_damage"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    VIRAL_NEGATIVE_CONTENT = "viral_negative_content"
    PLATFORM_POLICY_VIOLATION = "platform_policy_violation"
    CONTENT_CONTROVERSY = "content_controversy"
    INFLUENCER_SCANDAL = "influencer_scandal"
    BRAND_SAFETY_ISSUE = "brand_safety_issue"
    FAKE_NEWS_ASSOCIATION = "fake_news_association"
    COMPETITOR_ATTACK = "competitor_attack"
    TECHNICAL_CRISIS = "technical_crisis"
    PRIVACY_BREACH = "privacy_breach"
    HARASSMENT_INCIDENT = "harassment_incident"


class CrisisSeverity(str, Enum):
    """Crisis severity levels"""
    LOW = "low"                # Minor issue, routine monitoring
    MODERATE = "moderate"      # Requires attention and response
    HIGH = "high"             # Significant threat, immediate action
    CRITICAL = "critical"     # Severe crisis, emergency response
    CATASTROPHIC = "catastrophic"  # Existential threat


class ResponseStrategy(str, Enum):
    """Crisis response strategies"""
    MONITOR_ONLY = "monitor_only"
    DEFENSIVE_RESPONSE = "defensive_response"
    PROACTIVE_RESPONSE = "proactive_response"
    DAMAGE_CONTROL = "damage_control"
    FULL_CRISIS_MODE = "full_crisis_mode"
    STRATEGIC_SILENCE = "strategic_silence"
    TRANSPARENCY_APPROACH = "transparency_approach"
    LEGAL_RESPONSE = "legal_response"


class EscalationLevel(str, Enum):
    """Crisis escalation levels"""
    AUTOMATED = "automated"       # Handled by AI systems
    HUMAN_REVIEW = "human_review"  # Requires human review
    MANAGEMENT = "management"     # Escalated to management
    EXECUTIVE = "executive"       # CEO/senior leadership
    LEGAL = "legal"              # Legal team involvement
    PR_AGENCY = "pr_agency"      # External PR support


@dataclass
class CrisisDetectionRule:
    """Crisis detection rule configuration"""
    rule_id: str
    crisis_type: CrisisType
    severity_threshold: CrisisSeverity
    detection_criteria: Dict[str, Any]
    response_strategy: ResponseStrategy
    escalation_level: EscalationLevel
    enabled: bool = True
    platforms: List[str] = field(default_factory=lambda: ["all"])
    response_time_minutes: int = 15
    auto_response_enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResponseTemplate:
    """Crisis response template"""
    template_id: str
    crisis_type: CrisisType
    response_strategy: ResponseStrategy
    title: str
    content: str
    platforms: List[str]
    tone: str = "professional"  # professional, apologetic, defensive, transparent
    approval_required: bool = True
    auto_personalization: bool = True
    language_variants: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EscalationContact:
    """Crisis escalation contact information"""
    contact_id: str
    name: str
    role: str
    email: str
    phone: str
    escalation_levels: List[EscalationLevel]
    availability_hours: Dict[str, str] = field(default_factory=lambda: {
        "monday": "09:00-18:00",
        "tuesday": "09:00-18:00", 
        "wednesday": "09:00-18:00",
        "thursday": "09:00-18:00",
        "friday": "09:00-18:00",
        "saturday": "10:00-16:00",
        "sunday": "emergency_only"
    })
    timezone: str = "UTC"
    priority: int = 1  # 1 = highest priority
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AlertSettings:
    """Crisis alert configuration"""
    email_alerts: bool = True
    sms_alerts: bool = True
    slack_alerts: bool = True
    dashboard_alerts: bool = True
    email_recipients: List[str] = field(default_factory=list)
    sms_recipients: List[str] = field(default_factory=list)
    slack_channels: List[str] = field(default_factory=list)
    alert_frequency_minutes: int = 30
    duplicate_suppression: bool = True
    severity_filtering: List[CrisisSeverity] = field(default_factory=lambda: [
        CrisisSeverity.HIGH, CrisisSeverity.CRITICAL, CrisisSeverity.CATASTROPHIC
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MonitoringSettings:
    """Crisis monitoring configuration"""
    sentiment_monitoring: bool = True
    mention_monitoring: bool = True
    hashtag_monitoring: bool = True
    competitor_monitoring: bool = True
    news_monitoring: bool = True
    social_listening: bool = True
    
    # Monitoring thresholds
    sentiment_threshold: float = -0.3  # Negative sentiment threshold
    mention_spike_threshold: float = 3.0  # 3x normal mention volume
    hashtag_hijacking_threshold: float = 0.2  # 20% negative usage
    viral_negative_threshold: int = 10000  # Viral reach threshold
    
    # Monitoring frequencies
    real_time_monitoring: bool = True
    batch_analysis_hours: List[int] = field(default_factory=lambda: [6, 12, 18])
    deep_analysis_frequency: str = "daily"  # daily, weekly
    
    # Data sources
    platforms_to_monitor: List[str] = field(default_factory=lambda: [
        "twitter", "facebook", "instagram", "tiktok", "youtube", 
        "linkedin", "reddit", "discord", "telegram"
    ])
    news_sources: List[str] = field(default_factory=lambda: [
        "google_news", "bing_news", "reddit_news"
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CrisisConfig:
    """
    Comprehensive crisis management configuration
    Handles detection rules, response templates, escalation procedures
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "crisis_config.json"
        )
        
        # Core crisis settings
        self.detection_rules: Dict[str, CrisisDetectionRule] = {}
        self.response_templates: Dict[str, ResponseTemplate] = {}
        self.escalation_contacts: Dict[str, EscalationContact] = {}
        self.alert_settings = AlertSettings()
        self.monitoring_settings = MonitoringSettings()
        
        # Response configuration
        self.auto_response_enabled = False
        self.human_approval_required = True
        self.max_auto_response_severity = CrisisSeverity.MODERATE
        self.response_cooldown_hours = 2
        
        # Performance settings
        self.detection_sensitivity = 0.8  # 0.0 = low, 1.0 = high
        self.false_positive_tolerance = 0.1  # Acceptable false positive rate
        self.response_time_targets = {
            CrisisSeverity.LOW: 120,          # 2 hours
            CrisisSeverity.MODERATE: 60,      # 1 hour  
            CrisisSeverity.HIGH: 15,          # 15 minutes
            CrisisSeverity.CRITICAL: 5,       # 5 minutes
            CrisisSeverity.CATASTROPHIC: 2    # 2 minutes
        }
        
        # Initialize with defaults
        self._load_default_config()
        
        # Load saved configuration if exists
        if os.path.exists(self.config_path):
            self.load_config()
            
    def _load_default_config(self):
        """Load default crisis management configuration"""
        
        # Default detection rules
        default_rules = [
            CrisisDetectionRule(
                rule_id="reputation_damage_detection",
                crisis_type=CrisisType.REPUTATION_DAMAGE,
                severity_threshold=CrisisSeverity.HIGH,
                detection_criteria={
                    "sentiment_drop": -0.4,
                    "mention_volume_spike": 5.0,
                    "negative_keyword_density": 0.3
                },
                response_strategy=ResponseStrategy.DAMAGE_CONTROL,
                escalation_level=EscalationLevel.MANAGEMENT,
                response_time_minutes=15
            ),
            CrisisDetectionRule(
                rule_id="viral_negative_content",
                crisis_type=CrisisType.VIRAL_NEGATIVE_CONTENT,
                severity_threshold=CrisisSeverity.CRITICAL,
                detection_criteria={
                    "viral_reach": 50000,
                    "negative_engagement_ratio": 0.6,
                    "share_velocity": 100  # shares per minute
                },
                response_strategy=ResponseStrategy.FULL_CRISIS_MODE,
                escalation_level=EscalationLevel.EXECUTIVE,
                response_time_minutes=5
            ),
            CrisisDetectionRule(
                rule_id="platform_policy_violation",
                crisis_type=CrisisType.PLATFORM_POLICY_VIOLATION,
                severity_threshold=CrisisSeverity.HIGH,
                detection_criteria={
                    "policy_violation_confirmed": True,
                    "potential_account_suspension": True
                },
                response_strategy=ResponseStrategy.PROACTIVE_RESPONSE,
                escalation_level=EscalationLevel.LEGAL,
                response_time_minutes=10
            ),
            CrisisDetectionRule(
                rule_id="brand_safety_issue",
                crisis_type=CrisisType.BRAND_SAFETY_ISSUE,
                severity_threshold=CrisisSeverity.MODERATE,
                detection_criteria={
                    "brand_safety_score": 0.3,  # Below 30%
                    "inappropriate_content_association": True
                },
                response_strategy=ResponseStrategy.DEFENSIVE_RESPONSE,
                escalation_level=EscalationLevel.MANAGEMENT,
                response_time_minutes=30
            )
        ]
        
        for rule in default_rules:
            self.detection_rules[rule.rule_id] = rule
            
        # Default response templates
        default_templates = [
            ResponseTemplate(
                template_id="reputation_defense",
                crisis_type=CrisisType.REPUTATION_DAMAGE,
                response_strategy=ResponseStrategy.DAMAGE_CONTROL,
                title="Addressing Recent Concerns",
                content="We're aware of recent discussions and want to address them directly. We take all feedback seriously and are committed to maintaining the trust our community has placed in us. We're investigating the matter thoroughly and will provide updates as appropriate.",
                platforms=["twitter", "facebook", "instagram"],
                tone="professional"
            ),
            ResponseTemplate(
                template_id="policy_violation_response",
                crisis_type=CrisisType.PLATFORM_POLICY_VIOLATION,
                response_strategy=ResponseStrategy.TRANSPARENCY_APPROACH,
                title="Platform Policy Update",
                content="We've been notified of a policy concern on one of our platforms. We're working directly with the platform to resolve this matter and ensure full compliance with all guidelines. We remain committed to creating content that meets the highest standards.",
                platforms=["all"],
                tone="transparent"
            ),
            ResponseTemplate(
                template_id="brand_safety_clarification",
                crisis_type=CrisisType.BRAND_SAFETY_ISSUE,
                response_strategy=ResponseStrategy.PROACTIVE_RESPONSE,
                title="Our Brand Values Statement",
                content="We want to clarify our position and reaffirm our commitment to our core values. Any association with content that doesn't align with these values is not intentional and we're taking steps to ensure this doesn't happen in the future.",
                platforms=["linkedin", "twitter", "facebook"],
                tone="professional"
            )
        ]
        
        for template in default_templates:
            self.response_templates[template.template_id] = template
            
        # Default escalation contacts
        default_contacts = [
            EscalationContact(
                contact_id="crisis_manager",
                name="Crisis Manager",
                role="Crisis Management Lead",
                email="crisis@company.com",
                phone="+1-555-0100",
                escalation_levels=[EscalationLevel.HUMAN_REVIEW, EscalationLevel.MANAGEMENT],
                priority=1
            ),
            EscalationContact(
                contact_id="pr_director",
                name="PR Director", 
                role="Public Relations Director",
                email="pr@company.com",
                phone="+1-555-0101",
                escalation_levels=[EscalationLevel.MANAGEMENT, EscalationLevel.EXECUTIVE],
                priority=2
            ),
            EscalationContact(
                contact_id="legal_counsel",
                name="Legal Counsel",
                role="Legal Department",
                email="legal@company.com", 
                phone="+1-555-0102",
                escalation_levels=[EscalationLevel.LEGAL],
                priority=1
            )
        ]
        
        for contact in default_contacts:
            self.escalation_contacts[contact.contact_id] = contact
            
        logger.info(f"Loaded default crisis config: {len(default_rules)} rules, {len(default_templates)} templates")
        
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Load detection rules
            if 'detection_rules' in config_data:
                for rule_id, rule_data in config_data['detection_rules'].items():
                    self.detection_rules[rule_id] = CrisisDetectionRule(**rule_data)
                    
            # Load response templates
            if 'response_templates' in config_data:
                for template_id, template_data in config_data['response_templates'].items():
                    self.response_templates[template_id] = ResponseTemplate(**template_data)
                    
            # Load escalation contacts
            if 'escalation_contacts' in config_data:
                for contact_id, contact_data in config_data['escalation_contacts'].items():
                    self.escalation_contacts[contact_id] = EscalationContact(**contact_data)
                    
            # Load alert settings
            if 'alert_settings' in config_data:
                self.alert_settings = AlertSettings(**config_data['alert_settings'])
                
            # Load monitoring settings  
            if 'monitoring_settings' in config_data:
                self.monitoring_settings = MonitoringSettings(**config_data['monitoring_settings'])
                
            # Load other settings
            self.auto_response_enabled = config_data.get('auto_response_enabled', False)
            self.human_approval_required = config_data.get('human_approval_required', True)
            self.detection_sensitivity = config_data.get('detection_sensitivity', 0.8)
            self.false_positive_tolerance = config_data.get('false_positive_tolerance', 0.1)
            
            if 'response_time_targets' in config_data:
                self.response_time_targets = {
                    CrisisSeverity(k): v for k, v in config_data['response_time_targets'].items()
                }
                
            logger.info(f"Crisis configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load crisis config: {e}")
            return False
            
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'detection_rules': {
                    rule_id: rule.to_dict()
                    for rule_id, rule in self.detection_rules.items()
                },
                'response_templates': {
                    template_id: template.to_dict()
                    for template_id, template in self.response_templates.items()
                },
                'escalation_contacts': {
                    contact_id: contact.to_dict()
                    for contact_id, contact in self.escalation_contacts.items()
                },
                'alert_settings': self.alert_settings.to_dict(),
                'monitoring_settings': self.monitoring_settings.to_dict(),
                'auto_response_enabled': self.auto_response_enabled,
                'human_approval_required': self.human_approval_required,
                'max_auto_response_severity': self.max_auto_response_severity.value,
                'response_cooldown_hours': self.response_cooldown_hours,
                'detection_sensitivity': self.detection_sensitivity,
                'false_positive_tolerance': self.false_positive_tolerance,
                'response_time_targets': {
                    severity.value: minutes 
                    for severity, minutes in self.response_time_targets.items()
                },
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Crisis configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save crisis config: {e}")
            return False
            
    def add_detection_rule(self, rule: CrisisDetectionRule) -> bool:
        """Add a crisis detection rule"""
        try:
            self.detection_rules[rule.rule_id] = rule
            logger.info(f"Added crisis detection rule: {rule.rule_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add detection rule: {e}")
            return False
            
    def remove_detection_rule(self, rule_id: str) -> bool:
        """Remove a crisis detection rule"""
        try:
            if rule_id in self.detection_rules:
                del self.detection_rules[rule_id]
                logger.info(f"Removed crisis detection rule: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove detection rule: {e}")
            return False
            
    def add_response_template(self, template: ResponseTemplate) -> bool:
        """Add a crisis response template"""
        try:
            self.response_templates[template.template_id] = template
            logger.info(f"Added response template: {template.template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add response template: {e}")
            return False
            
    def get_response_template(self, crisis_type: CrisisType, 
                            response_strategy: ResponseStrategy) -> Optional[ResponseTemplate]:
        """Get appropriate response template for crisis type and strategy"""
        for template in self.response_templates.values():
            if (template.crisis_type == crisis_type and 
                template.response_strategy == response_strategy):
                return template
        return None
        
    def add_escalation_contact(self, contact: EscalationContact) -> bool:
        """Add an escalation contact"""
        try:
            self.escalation_contacts[contact.contact_id] = contact
            logger.info(f"Added escalation contact: {contact.contact_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add escalation contact: {e}")
            return False
            
    def get_escalation_contacts(self, level: EscalationLevel) -> List[EscalationContact]:
        """Get contacts for specific escalation level"""
        contacts = [
            contact for contact in self.escalation_contacts.values()
            if level in contact.escalation_levels
        ]
        # Sort by priority
        return sorted(contacts, key=lambda x: x.priority)
        
    def get_detection_rules_for_crisis(self, crisis_type: CrisisType) -> List[CrisisDetectionRule]:
        """Get all detection rules for a specific crisis type"""
        return [
            rule for rule in self.detection_rules.values()
            if rule.crisis_type == crisis_type and rule.enabled
        ]
        
    def update_monitoring_settings(self, **kwargs) -> bool:
        """Update monitoring settings"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.monitoring_settings, key):
                    setattr(self.monitoring_settings, key, value)
                    
            logger.info("Updated monitoring settings")
            return True
        except Exception as e:
            logger.error(f"Failed to update monitoring settings: {e}")
            return False
            
    def update_alert_settings(self, **kwargs) -> bool:
        """Update alert settings"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.alert_settings, key):
                    setattr(self.alert_settings, key, value)
                    
            logger.info("Updated alert settings")
            return True
        except Exception as e:
            logger.error(f"Failed to update alert settings: {e}")
            return False
            
    def get_response_time_target(self, severity: CrisisSeverity) -> int:
        """Get response time target for severity level"""
        return self.response_time_targets.get(severity, 60)  # Default 1 hour
        
    def should_auto_respond(self, crisis_type: CrisisType, severity: CrisisSeverity) -> bool:
        """Determine if crisis should trigger auto response"""
        if not self.auto_response_enabled:
            return False
            
        # Check if severity allows auto response
        severity_levels = [CrisisSeverity.LOW, CrisisSeverity.MODERATE, CrisisSeverity.HIGH, 
                          CrisisSeverity.CRITICAL, CrisisSeverity.CATASTROPHIC]
        
        max_auto_index = severity_levels.index(self.max_auto_response_severity)
        current_index = severity_levels.index(severity)
        
        if current_index > max_auto_index:
            return False
            
        # Check if rule allows auto response
        rules = self.get_detection_rules_for_crisis(crisis_type)
        for rule in rules:
            if rule.auto_response_enabled:
                return True
                
        return False
        
    def validate_config(self) -> List[str]:
        """Validate configuration and return issues"""
        issues = []
        
        # Validate detection rules
        for rule_id, rule in self.detection_rules.items():
            if not rule.detection_criteria:
                issues.append(f"Detection rule {rule_id} has no criteria")
                
            if rule.response_time_minutes <= 0:
                issues.append(f"Detection rule {rule_id} has invalid response time")
                
        # Validate response templates
        for template_id, template in self.response_templates.items():
            if not template.content.strip():
                issues.append(f"Response template {template_id} has no content")
                
            if not template.platforms:
                issues.append(f"Response template {template_id} has no platforms")
                
        # Validate escalation contacts
        for contact_id, contact in self.escalation_contacts.items():
            if not contact.email or not contact.phone:
                issues.append(f"Escalation contact {contact_id} missing contact info")
                
            if not contact.escalation_levels:
                issues.append(f"Escalation contact {contact_id} has no escalation levels")
                
        # Validate alert settings
        if (self.alert_settings.email_alerts and 
            not self.alert_settings.email_recipients):
            issues.append("Email alerts enabled but no recipients configured")
            
        if (self.alert_settings.sms_alerts and 
            not self.alert_settings.sms_recipients):
            issues.append("SMS alerts enabled but no recipients configured")
            
        # Validate monitoring settings
        if not self.monitoring_settings.platforms_to_monitor:
            issues.append("No platforms configured for monitoring")
            
        return issues
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'detection_rules': {
                rule_id: rule.to_dict()
                for rule_id, rule in self.detection_rules.items()
            },
            'response_templates': {
                template_id: template.to_dict()
                for template_id, template in self.response_templates.items()
            },
            'escalation_contacts': {
                contact_id: contact.to_dict()
                for contact_id, contact in self.escalation_contacts.items()
            },
            'alert_settings': self.alert_settings.to_dict(),
            'monitoring_settings': self.monitoring_settings.to_dict(),
            'auto_response_enabled': self.auto_response_enabled,
            'human_approval_required': self.human_approval_required,
            'detection_sensitivity': self.detection_sensitivity,
            'false_positive_tolerance': self.false_positive_tolerance,
            'response_time_targets': {
                severity.value: minutes 
                for severity, minutes in self.response_time_targets.items()
            }
        }


# Create global configuration instance
crisis_config = CrisisConfig()


# Export main classes and instance
__all__ = [
    'CrisisConfig',
    'CrisisDetectionRule',
    'ResponseTemplate',
    'EscalationContact',
    'AlertSettings',
    'MonitoringSettings',
    'CrisisType',
    'CrisisSeverity',
    'ResponseStrategy',
    'EscalationLevel',
    'crisis_config'
]