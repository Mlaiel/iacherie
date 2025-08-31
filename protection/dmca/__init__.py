"""🚨 DMCA Automation Module - Enterprise Content Protection
=========================================================

Professional DMCA automation system for multi-format content protection.
Supports audio, video, image, and text content with AI-powered evidence compilation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚠️  LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
====================================================
This software and all associated concepts, algorithms, and implementations are the
exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).

Any unauthorized use, reproduction, distribution, or derivation of this work without
explicit written permission from Fahed Mlaiel is strictly prohibited and may result in:
- Immediate legal action under German and International copyright law
- Claims for damages and lost profits
- Injunctive relief to prevent further infringement
- Criminal prosecution where applicable

Contact: mlaiel@live.de for licensing inquiries.

Project Team Specialties:
- Lead AI Developer & Architect: Advanced ML/AI systems
- Backend Senior Engineer: Enterprise Python/FastAPI systems
- DevOps Engineer: Kubernetes/Cloud infrastructure
- Security Specialist: Cybersecurity & legal compliance
- Audio Processing Engineer: Digital signal processing
- Database Administrator: High-performance data systems
- Microservices Architect: Distributed systems design
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import json
import re
import aiohttp
import jinja2
from pathlib import Path
import hashlib
import uuid
import secrets
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

# Import new modules
try:
    from .template_engine import TemplateContext, DMCATemplateEngine, create_template_engine
except ImportError:
    logger.warning("Template engine module not available")
    TemplateContext = None
    DMCATemplateEngine = None
    create_template_engine = None

try:
    from .security_auditor import (
        ComplianceLevel, SecurityAuditResult, ComplianceFramework,
        SecurityAuditReport, ComplianceValidation, DMCASecurityAuditor,
        create_security_auditor
    )
except ImportError:
    logger.warning("Security auditor module not available")
    ComplianceLevel = None
    SecurityAuditResult = None
    ComplianceFramework = None
    SecurityAuditReport = None
    ComplianceValidation = None
    DMCASecurityAuditor = None
    create_security_auditor = None

try:
    from .performance_analyzer import (
        MetricType, TimeFrame, PerformanceIndicator, PerformanceMetric,
        AnalyticsReport, PlatformPerformance, TrendAnalysis,
        DMCAPerformanceAnalyzer, create_performance_analyzer
    )
except ImportError:
    logger.warning("Performance analyzer module not available")
    MetricType = None
    TimeFrame = None
    PerformanceIndicator = None
    PerformanceMetric = None
    AnalyticsReport = None
    PlatformPerformance = None
    TrendAnalysis = None
    DMCAPerformanceAnalyzer = None
    create_performance_analyzer = None

logger = logging.getLogger(__name__)

Base = declarative_base()


class DMCAStatus(Enum):
    """Professional DMCA procedure status tracking"""
    PENDING = "pending"
    ANALYSIS_REQUIRED = "analysis_required"
    EVIDENCE_GATHERING = "evidence_gathering"
    LEGAL_REVIEW = "legal_review"
    READY_TO_SEND = "ready_to_send"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    COMPLIANCE_REQUIRED = "compliance_required"
    COMPLIED = "complied"
    PARTIALLY_COMPLIED = "partially_complied"
    DISPUTED = "disputed"
    COUNTER_CLAIMED = "counter_claimed"
    ESCALATED = "escalated"
    LEGAL_ACTION = "legal_action"
    SETTLED = "settled"
    FAILED = "failed"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class DMCAPriority(IntEnum):
    """DMCA case priority levels"""
    LOW = 1           # Minor infringement, non-commercial
    MEDIUM = 2        # Standard commercial infringement
    HIGH = 3          # Large-scale commercial infringement
    URGENT = 4        # Viral content, major revenue impact
    CRITICAL = 5      # Legal threats, massive infringement


class NotificationType(Enum):
    """Enhanced DMCA notification types"""
    TAKEDOWN_REQUEST = "takedown_request"
    TAKEDOWN_URGENT = "takedown_urgent"
    COUNTER_NOTICE = "counter_notice"
    COUNTER_RESPONSE = "counter_response"
    ESCALATION_FORMAL = "escalation_formal"
    ESCALATION_LEGAL = "escalation_legal"
    COMPLIANCE_REPORT = "compliance_report"
    SETTLEMENT_OFFER = "settlement_offer"
    CEASE_DESIST = "cease_desist"
    FINAL_WARNING = "final_warning"
    LEGAL_ACTION_NOTICE = "legal_action_notice"


class ContentType(Enum):
    """Supported content types for DMCA protection"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    MIXED_MEDIA = "mixed_media"


class PlatformType(Enum):
    """Enhanced platform support"""
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    INSTAGRAM = "instagram"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    REDDIT = "reddit"
    GENERIC_WEB = "generic_web"


class EvidenceType(Enum):
    """Types of evidence for DMCA claims"""
    AUDIO_FINGERPRINT = "audio_fingerprint"
    VIDEO_FINGERPRINT = "video_fingerprint"
    IMAGE_HASH = "image_hash"
    TEXT_SIMILARITY = "text_similarity"
    METADATA_ANALYSIS = "metadata_analysis"
    TIMESTAMP_PROOF = "timestamp_proof"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    USAGE_ANALYTICS = "usage_analytics"
    REVENUE_IMPACT = "revenue_impact"
    SCREENSHOT = "screenshot"
    VIDEO_CAPTURE = "video_capture"
    WITNESS_STATEMENT = "witness_statement"


class LegalJurisdiction(Enum):
    """Legal jurisdictions for DMCA compliance"""
    US_FEDERAL = "us_federal"
    EU_GDPR = "eu_gdpr"
    UK_COPYRIGHT = "uk_copyright"
    CANADA_COPYRIGHT = "canada_copyright"
    AUSTRALIA_COPYRIGHT = "australia_copyright"
    GERMANY_UrhG = "germany_urhg"
    FRANCE_CPI = "france_cpi"
    INTERNATIONAL = "international"


@dataclass
class DMCAEvidence:
    """Professional evidence compilation for DMCA claims"""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType = EvidenceType.SCREENSHOT
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    similarity_score: Optional[float] = None
    detection_timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "pending"
    legal_admissible: bool = False
    
    def calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash for evidence integrity"""
        return hashlib.sha256(content).hexdigest()


@dataclass
class DMCAContentInfo:
    """Original content information for DMCA claims"""
    content_id: str
    title: str
    content_type: ContentType
    creator_name: str
    creator_contact: str
    creation_date: datetime
    publication_date: Optional[datetime] = None
    copyright_notice: Optional[str] = None
    registration_number: Optional[str] = None
    fingerprint_hash: Optional[str] = None
    original_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None  # in seconds for audio/video
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DMCAInfringement:
    """Infringing content details"""
    infringement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    infringing_url: str = ""
    platform: PlatformType = PlatformType.GENERIC_WEB
    uploader_name: Optional[str] = None
    uploader_contact: Optional[str] = None
    upload_date: Optional[datetime] = None
    discovery_date: datetime = field(default_factory=datetime.utcnow)
    content_title: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    revenue_estimate: Optional[float] = None
    evidence_list: List[DMCAEvidence] = field(default_factory=list)
    similarity_analysis: Dict[str, Any] = field(default_factory=dict)
    commercial_use: bool = False
    viral_status: bool = False


class DMCANoticeModel(Base):
    """SQLAlchemy model for DMCA notices database storage"""
    __tablename__ = "dmca_notices"
    
    id = Column(Integer, primary_key=True)
    notice_id = Column(String(50), unique=True, nullable=False)
    case_id = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Status and priority
    status = Column(String(30), default=DMCAStatus.PENDING.value)
    priority = Column(Integer, default=DMCAPriority.MEDIUM.value)
    notification_type = Column(String(30), nullable=False)
    
    # Content information
    original_content = Column(JSON)
    infringing_content = Column(JSON)
    evidence_package = Column(JSON)
    
    # Legal information
    jurisdiction = Column(String(30), default=LegalJurisdiction.US_FEDERAL.value)
    legal_basis = Column(Text)
    damages_claimed = Column(Float)
    
    # Platform information
    platform = Column(String(30), nullable=False)
    platform_contact = Column(JSON)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    response_deadline = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Response tracking
    response_received = Column(Boolean, default=False)
    compliance_achieved = Column(Boolean, default=False)
    escalation_count = Column(Integer, default=0)
    
    # Documents
    notice_document_path = Column(String(500))
    response_document_path = Column(String(500))
    
    # Metrics
    response_time_hours = Column(Float)
    resolution_time_hours = Column(Float)
    success_rate = Column(Float)


class DMCACaseModel(Base):
    """SQLAlchemy model for DMCA cases (can contain multiple notices)"""
    __tablename__ = "dmca_cases"
    
    id = Column(Integer, primary_key=True)
    case_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Case information
    case_title = Column(String(200), nullable=False)
    case_description = Column(Text)
    original_content_id = Column(String(100), nullable=False)
    
    # Status tracking
    status = Column(String(30), default=DMCAStatus.PENDING.value)
    priority = Column(Integer, default=DMCAPriority.MEDIUM.value)
    
    # Metrics
    total_infringements = Column(Integer, default=0)
    notices_sent = Column(Integer, default=0)
    successful_takedowns = Column(Integer, default=0)
    revenue_recovered = Column(Float, default=0.0)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    estimated_resolution = Column(DateTime)
    
    # Legal tracking
    legal_counsel_involved = Column(Boolean, default=False)
    settlement_amount = Column(Float)
    court_case_number = Column(String(100))


# Export all important classes and enums
__all__ = [
    # Core enums and models
    'DMCAStatus',
    'DMCAPriority', 
    'NotificationType',
    'ContentType',
    'PlatformType',
    'EvidenceType',
    'LegalJurisdiction',
    'DMCAEvidence',
    'DMCAContentInfo',
    'DMCAInfringement',
    'DMCANoticeModel',
    'DMCACaseModel',
    'Base',
    
    # Template engine
    'TemplateContext',
    'DMCATemplateEngine',
    'create_template_engine',
    
    # Security auditor
    'ComplianceLevel',
    'SecurityAuditResult',
    'ComplianceFramework',
    'SecurityAuditReport',
    'ComplianceValidation',
    'DMCASecurityAuditor',
    'create_security_auditor',
    
    # Performance analyzer
    'MetricType',
    'TimeFrame',
    'PerformanceIndicator',
    'PerformanceMetric',
    'AnalyticsReport',
    'PlatformPerformance',
    'TrendAnalysis',
    'DMCAPerformanceAnalyzer',
    'create_performance_analyzer',
    
    # Factory classes
    'DMCAFactory',
    'DMCASystem',
    'create_dmca_system'
]
    TWITTER = "twitter"
    GENERIC_WEB = "generic_web"


@dataclass
class ContactInfo:
    """Informations de contact pour les notifications DMCA"""
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None


@dataclass
class InfringementEvidence:
    """Preuves d'infraction pour DMCA"""
    original_url: str
    infringing_url: str
    similarity_score: float
    fingerprint_match: bool
    timestamp_detected: datetime
    screenshots: List[str]
    metadata: Dict[str, Any]


class DMCANotice(BaseModel):
    """Modèle de notification DMCA"""
    id: str = Field(..., description="ID unique de la notification")
    type: NotificationType
    status: DMCAStatus = DMCAStatus.PENDING
    platform: PlatformType
    infringement_evidence: Dict[str, Any]
    copyright_owner: Dict[str, Any]
    agent_contact: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('response_deadline', pre=True, always=True)
    def set_response_deadline(cls, v, values):
        if v is None and values.get('sent_at'):
            return values['sent_at'] + timedelta(days=14)
        return v


class PlatformContact(BaseModel):
    """Contact information for platform DMCA agents"""
    platform: PlatformType
    name: str
    email: str
    dmca_portal_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    form_url: Optional[str] = None
    special_instructions: Optional[str] = None
    response_time_days: int = 14


class DMCAFactory:
    """
    🏭 Enterprise DMCA Factory - Complete System Builder
    =================================================
    
    Central factory for creating and managing all DMCA system components.
    Provides enterprise-grade initialization and configuration management.
    """
    
    @classmethod
    def create_complete_system(cls, db_session=None, config: Optional[Dict[str, Any]] = None):
        """Create complete DMCA automation system"""
        system_components = {}
        
        # Core components
        if create_template_engine:
            system_components['template_engine'] = create_template_engine()
        
        if create_security_auditor:
            encryption_key = config.get('encryption_key') if config else None
            system_components['security_auditor'] = create_security_auditor(encryption_key)
        
        if create_performance_analyzer:
            system_components['performance_analyzer'] = create_performance_analyzer()
        
        # Import and create other components
        try:
            from .notice_generator import create_notice_generator
            system_components['notice_generator'] = create_notice_generator()
        except ImportError:
            logger.warning("Notice generator not available")
        
        try:
            from .legal_compliance import create_compliance_validator
            system_components['compliance_validator'] = create_compliance_validator()
        except ImportError:
            logger.warning("Compliance validator not available")
        
        try:
            from .automated_validator import create_automated_validator
            system_components['automated_validator'] = create_automated_validator()
        except ImportError:
            logger.warning("Automated validator not available")
        
        try:
            from .escalation_manager import create_escalation_manager
            system_components['escalation_manager'] = create_escalation_manager()
        except ImportError:
            logger.warning("Escalation manager not available")
        
        try:
            from .platform_integration import create_platform_integrator
            system_components['platform_integrator'] = create_platform_integrator()
        except ImportError:
            logger.warning("Platform integrator not available")
        
        try:
            from .response_tracker import create_response_tracker
            system_components['response_tracker'] = create_response_tracker()
        except ImportError:
            logger.warning("Response tracker not available")
        
        try:
            from .orchestration_engine import create_orchestration_engine
            system_components['orchestration_engine'] = create_orchestration_engine()
        except ImportError:
            logger.warning("Orchestration engine not available")
        
        try:
            from .collaboration_intelligence import create_collaboration_intelligence
            system_components['collaboration_intelligence'] = create_collaboration_intelligence()
        except ImportError:
            logger.warning("Collaboration intelligence not available")
        
        try:
            from .response_intelligence import create_response_intelligence
            system_components['response_intelligence'] = create_response_intelligence()
        except ImportError:
            logger.warning("Response intelligence not available")
        
        return DMCASystem(components=system_components, db_session=db_session)
    
    @classmethod
    def create_template_engine(cls):
        """Create template engine component"""
        if create_template_engine:
            return create_template_engine()
        return None
    
    @classmethod
    def create_security_auditor(cls, encryption_key: Optional[str] = None):
        """Create security auditor component"""
        if create_security_auditor:
            return create_security_auditor(encryption_key)
        return None
    
    @classmethod
    def create_performance_analyzer(cls):
        """Create performance analyzer component"""
        if create_performance_analyzer:
            return create_performance_analyzer()
        return None


class DMCASystem:
    """
    🎯 Complete DMCA Automation System
    ================================
    
    Integrated system managing all DMCA operations with enterprise-grade
    coordination between all components.
    """
    
    def __init__(self, components: Dict[str, Any], db_session=None):
        self.components = components
        self.db_session = db_session
        self.is_initialized = bool(components)
        
        # System metadata
        self.system_id = f"DMCA_SYS_{int(datetime.utcnow().timestamp())}"
        self.created_at = datetime.utcnow()
        self.version = "2.0.0"
        
        logger.info(f"DMCA System {self.system_id} initialized with {len(components)} components")
    
    def get_component(self, component_name: str):
        """Get specific system component"""
        return self.components.get(component_name)
    
    async def process_dmca_case(
        self,
        original_content: DMCAContentInfo,
        infringement: DMCAInfringement,
        priority: DMCAPriority = DMCAPriority.MEDIUM,
        automation_level: str = "full"
    ):
        """Process complete DMCA case through the system"""
        case_id = f"CASE_{secrets.token_hex(8).upper()}"
        
        logger.info(f"Processing DMCA case {case_id} with priority {priority.name}")
        
        try:
            # 1. Validate evidence
            if 'automated_validator' in self.components:
                validation_result = await self.components['automated_validator'].validate_claim(
                    original_content, infringement
                )
                if not validation_result.is_valid:
                    logger.warning(f"Case {case_id} failed validation: {validation_result.issues}")
                    return {"status": "validation_failed", "issues": validation_result.issues}
            
            # 2. Generate DMCA notice
            if 'template_engine' in self.components and 'notice_generator' in self.components:
                notice = await self.components['notice_generator'].generate_professional_notice(
                    original_content, infringement, priority
                )
            
            # 3. Security audit
            if 'security_auditor' in self.components:
                case_data = {
                    "case_id": case_id,
                    "original_content": original_content.__dict__,
                    "infringement": infringement.__dict__,
                    "priority": priority.value
                }
                audit_result = await self.components['security_auditor'].perform_comprehensive_audit(case_data)
                
                if audit_result.overall_result == SecurityAuditResult.CRITICAL:
                    logger.error(f"Case {case_id} failed security audit")
                    return {"status": "security_failed", "audit_result": audit_result}
            
            # 4. Platform integration
            if 'platform_integrator' in self.components:
                submission_result = await self.components['platform_integrator'].submit_notice(
                    infringement.platform, notice
                )
            
            # 5. Track response
            if 'response_tracker' in self.components:
                tracking = await self.components['response_tracker'].start_tracking(case_id)
            
            # 6. Performance monitoring
            if 'performance_analyzer' in self.components:
                self.components['performance_analyzer'].metrics_history.append(
                    PerformanceMetric(
                        metric_type=MetricType.SUCCESS_RATE,
                        value=1.0,  # Successful initiation
                        unit="boolean",
                        timestamp=datetime.utcnow(),
                        context={"case_id": case_id}
                    )
                )
            
            return {
                "status": "success",
                "case_id": case_id,
                "notice_generated": 'notice_generator' in self.components,
                "security_audit_passed": 'security_auditor' in self.components,
                "platform_submitted": 'platform_integrator' in self.components,
                "tracking_started": 'response_tracker' in self.components
            }
            
        except Exception as e:
            logger.error(f"Failed to process DMCA case {case_id}: {str(e)}")
            return {"status": "error", "case_id": case_id, "error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        component_status = {}
        for name, component in self.components.items():
            component_status[name] = {
                "available": component is not None,
                "type": type(component).__name__ if component else None,
                "status": "operational" if component else "unavailable"
            }
        
        return {
            "system_id": self.system_id,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "is_initialized": self.is_initialized,
            "total_components": len(self.components),
            "components": component_status,
            "uptime": (datetime.utcnow() - self.created_at).total_seconds()
        }


# Additional helper functions
def create_dmca_system(db_session=None, config: Optional[Dict[str, Any]] = None) -> DMCASystem:
    """Factory function to create complete DMCA system"""
    return DMCAFactory.create_complete_system(db_session, config)


class DMCATemplate:
    """Générateur de templates DMCA professionnels"""
    
    def __init__(self):
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_templates())
        )
    
    def _get_templates(self) -> Dict[str, str]:
        """Templates professionnels pour notifications DMCA"""
        return {
            'takedown_notice': """Subject: DMCA Takedown Notice - Copyright Infringement

To Whom It May Concern:

I am writing to notify you of copyright infringement occurring on your platform. This notice is submitted pursuant to Section 512(c) of the Digital Millennium Copyright Act ("DMCA").

IDENTIFICATION OF COPYRIGHTED WORK:
The copyrighted work that has been infringed is:
- Title: {{ original_work.title }}
- Author/Owner: {{ copyright_owner.name }}
- Description: {{ original_work.description }}
- Original URL: {{ original_work.url }}
- Copyright Registration: {{ original_work.registration_number | default("Pending") }}

IDENTIFICATION OF INFRINGING MATERIAL:
The following material on your platform infringes the above copyright:
- Infringing URL: {{ infringing_content.url }}
- Platform: {{ platform }}
- Description: {{ infringing_content.description }}
- Upload Date: {{ infringing_content.upload_date }}
- Similarity Score: {{ evidence.similarity_score }}%

GOOD FAITH BELIEF:
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY AND AUTHORITY:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.

CONTACT INFORMATION:
{{ copyright_owner.name }}
{{ copyright_owner.email }}
{{ copyright_owner.phone | default("") }}
{{ copyright_owner.address | default("") }}

AGENT CONTACT:
{{ agent.name }}
{{ agent.email }}
{{ agent.phone | default("") }}

REQUEST FOR ACTION:
I request that you remove or disable access to the infringing material immediately. Please confirm receipt of this notice and provide confirmation of the removal within {{ response_time_days }} business days.

Electronic Signature: {{ copyright_owner.name }}
Date: {{ current_date }}

This notice is submitted in good faith and I understand that any misrepresentation may result in liability for damages.
            """,
            
            'counter_notice_response': """Subject: Re: DMCA Counter-Notice Response

Dear {{ sender_name }},

We acknowledge receipt of your counter-notice dated {{ counter_notice_date }} regarding the DMCA takedown notice we submitted on {{ original_notice_date }}.

After careful review of your counter-notice and the evidence provided, we maintain our position that the material in question infringes our copyright for the following reasons:

{{ detailed_response }}

NEXT STEPS:
As permitted under Section 512(g) of the DMCA, we intend to file a lawsuit seeking a court order to restrain the allegedly infringing activity. We will notify the platform provider within 10 business days if we choose to pursue legal action.

EVIDENCE:
We have documented evidence including:
- Original creation timestamps
- Copyright registration documentation
- Technical fingerprint analysis showing {{ similarity_percentage }}% match
- Chain of title documentation

We remain open to discussion to resolve this matter amicably. Please contact our legal department at {{ legal_contact.email }} within {{ response_deadline }} to discuss potential resolution.

Best regards,
{{ copyright_owner.name }}
{{ agent.name }}, Authorized Agent
            """,
            
            'escalation_notice': """Subject: DMCA Escalation - Failure to Respond to Takedown Notice

To Whom It May Concern:

This notice serves as an escalation of our DMCA takedown notice dated {{ original_notice_date }} (Reference: {{ notice_id }}).

TIMELINE:
- Original Notice Sent: {{ original_notice_date }}
- Response Deadline: {{ response_deadline }}
- Current Date: {{ current_date }}
- Days Overdue: {{ days_overdue }}

LACK OF RESPONSE:
Despite the statutory requirement to respond to valid DMCA notices, we have not received:
1. Acknowledgment of receipt
2. Action taken on the infringing content
3. Communication regarding the status of our request

CURRENT STATUS:
The infringing material remains accessible at:
{{ infringing_urls }}

LEGAL IMPLICATIONS:
Your platform's failure to respond to valid DMCA notices may result in:
- Loss of safe harbor protections under Section 512(c)
- Direct liability for copyright infringement
- Potential legal action for willful copyright infringement

IMMEDIATE ACTION REQUIRED:
We demand immediate removal of the infringing content and written confirmation within 48 hours. Failure to comply will result in:
- Formal legal proceedings
- Reporting to relevant authorities
- Public disclosure of non-compliance

This escalation is sent in good faith and pursuant to our rights under copyright law.

{{ copyright_owner.name }}
{{ agent.name }}, Authorized Agent
Date: {{ current_date }}
            """
        }
    
    def generate_notice(self, template_name: str, context: Dict[str, Any]) -> str:
        """Génère une notification DMCA à partir d'un template"""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context, current_date=datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            logger.error(f"Erreur génération template DMCA {template_name}: {e}")
            raise


class DMCAAutomationService:
    """Service professionnel d'automatisation DMCA"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.template_generator = DMCATemplate()
        self.active_notices: Dict[str, DMCANotice] = {}
        self.platform_contacts: Dict[PlatformType, PlatformContact] = {}
        self.email_client = None
        self.running = False
        
        # Configuration par défaut
        self.default_config = {
            'auto_send_enabled': False,
            'escalation_days': 14,
            'max_retries': 3,
            'retry_delay_hours': 24,
            'require_manual_approval': True,
            'track_responses': True,
            'generate_reports': True
        }
        
        self._setup_platform_contacts()
    
    def _setup_platform_contacts(self):
        """Configure les contacts DMCA des plateformes principales"""
        contacts = [
            PlatformContact(
                platform=PlatformType.YOUTUBE,
                name="YouTube Copyright Team",
                email="copyright@youtube.com",
                dmca_portal_url="https://www.youtube.com/copyright_complaint_form",
                response_time_days=7
            ),
            PlatformContact(
                platform=PlatformType.SPOTIFY,
                name="Spotify Copyright Team",
                email="copyright@spotify.com",
                form_url="https://support.spotify.com/contact-spotify-support/",
                response_time_days=10
            ),
            PlatformContact(
                platform=PlatformType.SOUNDCLOUD,
                name="SoundCloud Copyright",
                email="copyright@soundcloud.com",
                dmca_portal_url="https://soundcloud.com/imprint",
                response_time_days=14
            ),
            PlatformContact(
                platform=PlatformType.INSTAGRAM,
                name="Meta Copyright Team",
                email="ip@meta.com",
                form_url="https://help.instagram.com/contact/372592039493026",
                response_time_days=7
            ),
            PlatformContact(
                platform=PlatformType.TIKTOK,
                name="TikTok Copyright Team",
                email="copyright@tiktok.com",
                form_url="https://www.tiktok.com/legal/copyright-policy",
                response_time_days=10
            )
        ]
        
        for contact in contacts:
            self.platform_contacts[contact.platform] = contact
    
    async def initialize(self) -> bool:
        """Initialise le service DMCA"""
        try:
            logger.info("Initialisation du service DMCA...")
            
            # Initialisation du client email
            await self._setup_email_client()
            
            # Chargement des notices en cours
            await self._load_active_notices()
            
            # Démarrage du monitoring des réponses
            if self.config.get('track_responses', True):
                asyncio.create_task(self._monitor_responses())
            
            # Démarrage de l'escalation automatique
            asyncio.create_task(self._auto_escalation_monitor())
            
            self.running = True
            logger.info("Service DMCA initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation service DMCA: {e}")
            return False
    
    async def _setup_email_client(self):
        """Configure le client email pour l'envoi automatique"""
        try:
            # Configuration SMTP selon la config
            smtp_config = self.config.get('smtp', {})
            if smtp_config:
                # Configure asyncio SMTP client
                self.smtp_host = smtp_config.get('host', 'localhost')
                self.smtp_port = smtp_config.get('port', 587)
                self.smtp_user = smtp_config.get('user', '')
                self.smtp_password = smtp_config.get('password', '')
                self.smtp_tls = smtp_config.get('tls', True)
                logger.info("Email client configured with SMTP settings")
            else:
                logger.warning("Aucune configuration SMTP - mode manuel uniquement")
        except Exception as e:
            logger.error(f"Erreur configuration email: {e}")
    
    async def create_dmca_notice(
        self,
        infringement_evidence: InfringementEvidence,
        copyright_owner: ContactInfo,
        agent_contact: ContactInfo,
        platform: PlatformType,
        notice_type: NotificationType = NotificationType.TAKEDOWN
    ) -> DMCANotice:
        """Crée une nouvelle notification DMCA"""
        try:
            notice_id = self._generate_notice_id()
            
            notice = DMCANotice(
                id=notice_id,
                type=notice_type,
                platform=platform,
                infringement_evidence={
                    'original_url': infringement_evidence.original_url,
                    'infringing_url': infringement_evidence.infringing_url,
                    'similarity_score': infringement_evidence.similarity_score,
                    'fingerprint_match': infringement_evidence.fingerprint_match,
                    'detection_timestamp': infringement_evidence.timestamp_detected.isoformat(),
                    'screenshots': infringement_evidence.screenshots,
                    'metadata': infringement_evidence.metadata
                },
                copyright_owner={
                    'name': copyright_owner.name,
                    'email': copyright_owner.email,
                    'phone': copyright_owner.phone,
                    'address': copyright_owner.address,
                    'company': copyright_owner.company
                },
                agent_contact={
                    'name': agent_contact.name,
                    'email': agent_contact.email,
                    'phone': agent_contact.phone,
                    'address': agent_contact.address,
                    'company': agent_contact.company
                }
            )
            
            self.active_notices[notice_id] = notice
            
            logger.info(f"Notice DMCA créée: {notice_id} pour {platform.value}")
            return notice
            
        except Exception as e:
            logger.error(f"Erreur création notice DMCA: {e}")
            raise
    
    async def generate_notice_content(self, notice_id: str) -> str:
        """Génère le contenu textuel de la notification DMCA"""
        try:
            notice = self.active_notices.get(notice_id)
            if not notice:
                raise ValueError(f"Notice {notice_id} non trouvée")
            
            # Préparation du contexte pour le template
            context = {
                'notice_id': notice.id,
                'platform': notice.platform.value,
                'original_work': {
                    'title': notice.infringement_evidence.get('metadata', {}).get('title', 'Non spécifié'),
                    'url': notice.infringement_evidence['original_url'],
                    'description': notice.infringement_evidence.get('metadata', {}).get('description', ''),
                    'registration_number': notice.infringement_evidence.get('metadata', {}).get('copyright_reg', None)
                },
                'infringing_content': {
                    'url': notice.infringement_evidence['infringing_url'],
                    'description': notice.infringement_evidence.get('metadata', {}).get('infringing_description', ''),
                    'upload_date': notice.infringement_evidence.get('metadata', {}).get('upload_date', 'Inconnu')
                },
                'evidence': {
                    'similarity_score': notice.infringement_evidence['similarity_score']
                },
                'copyright_owner': notice.copyright_owner,
                'agent': notice.agent_contact,
                'response_time_days': self.platform_contacts.get(notice.platform, PlatformContact(
                    platform=notice.platform, name="", email=""
                )).response_time_days
            }
            
            # Sélection du template selon le type
            template_name = 'takedown_notice'
            if notice.type == NotificationType.COUNTER_NOTICE:
                template_name = 'counter_notice_response'
            elif notice.type == NotificationType.ESCALATION:
                template_name = 'escalation_notice'
            
            content = self.template_generator.generate_notice(template_name, context)
            
            logger.info(f"Contenu généré pour notice {notice_id}")
            return content
            
        except Exception as e:
            logger.error(f"Erreur génération contenu notice {notice_id}: {e}")
            raise
    
    async def send_notice(self, notice_id: str, auto_send: bool = False) -> bool:
        """Envoie une notification DMCA"""
        try:
            notice = self.active_notices.get(notice_id)
            if not notice:
                raise ValueError(f"Notice {notice_id} non trouvée")
            
            # Vérification des permissions d'envoi automatique
            if auto_send and not self.config.get('auto_send_enabled', False):
                logger.warning(f"Envoi automatique désactivé pour notice {notice_id}")
                return False
            
            # Vérification de l'approbation manuelle
            if self.config.get('require_manual_approval', True) and not auto_send:
                logger.info(f"Approbation manuelle requise pour notice {notice_id}")
                return False
            
            # Récupération du contact de la plateforme
            platform_contact = self.platform_contacts.get(notice.platform)
            if not platform_contact:
                logger.error(f"Contact non configuré pour plateforme {notice.platform.value}")
                return False
            
            # Génération du contenu
            content = await self.generate_notice_content(notice_id)
            
            # Envoi selon la méthode préférée de la plateforme
            success = False
            if platform_contact.api_endpoint:
                success = await self._send_via_api(notice, platform_contact, content)
            elif platform_contact.email:
                success = await self._send_via_email(notice, platform_contact, content)
            elif platform_contact.form_url:
                success = await self._send_via_form(notice, platform_contact, content)
            
            if success:
                notice.status = DMCAStatus.SENT
                notice.sent_at = datetime.utcnow()
                notice.response_deadline = notice.sent_at + timedelta(days=platform_contact.response_time_days)
                
                logger.info(f"Notice DMCA {notice_id} envoyée avec succès à {notice.platform.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur envoi notice DMCA {notice_id}: {e}")
            return False
    
    async def _send_via_email(self, notice: DMCANotice, contact: PlatformContact, content: str) -> bool:
        """Envoie la notification par email"""
        try:
            if not self.email_client:
                logger.error("Client email non configuré")
                return False
            
            # Implementation: Send email with SMTP client
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.smtp_user
                msg['To'] = contact.email
                msg['Subject'] = f"DMCA {notice.type.value.title()} Notice - {notice.id}"
                
                msg.attach(MIMEText(content, 'html'))
                
                # Send via SMTP
                if hasattr(self, 'smtp_host'):
                    server = smtplib.SMTP(self.smtp_host, getattr(self, 'smtp_port', 587))
                    if getattr(self, 'smtp_tls', True):
                        server.starttls()
                    if getattr(self, 'smtp_user', '') and getattr(self, 'smtp_password', ''):
                        server.login(self.smtp_user, self.smtp_password)
                    
                    server.send_message(msg)
                    server.quit()
                    
                    logger.info(f"DMCA notice sent via email to {contact.email}")
                    return True
                else:
                    logger.warning("SMTP not configured - email sending skipped")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                return False
            #     body=content
            # )
            
            logger.info(f"Email DMCA envoyé à {contact.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email DMCA: {e}")
            return False
    
    async def _send_via_api(self, notice: DMCANotice, contact: PlatformContact, content: str) -> bool:
        """Envoie la notification via API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'notice_id': notice.id,
                    'type': notice.type.value,
                    'content': content,
                    'infringement_url': notice.infringement_evidence['infringing_url'],
                    'copyright_owner': notice.copyright_owner
                }
                
                async with session.post(contact.api_endpoint, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"API DMCA envoyée à {contact.platform.value}")
                        return True
                    else:
                        logger.error(f"Erreur API DMCA: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Erreur envoi API DMCA: {e}")
            return False
    
    async def _send_via_form(self, notice: DMCANotice, contact: PlatformContact, content: str) -> bool:
        """Soumet la notification via formulaire web"""
        try:
            # Implementation with web form submission
            try:
                # Basic implementation using requests/aiohttp for form submission
                if contact.form_url:
                    async with aiohttp.ClientSession() as session:
                        form_data = {
                            'notice_content': content,
                            'notice_type': notice.type.value,
                            'content_url': notice.infringing_urls[0] if notice.infringing_urls else '',
                            'submitter_name': 'DMCA Automation System',
                            'submitter_email': getattr(self, 'smtp_user', 'dmca@example.com')
                        }
                        
                        async with session.post(contact.form_url, data=form_data) as response:
                            if response.status == 200:
                                logger.info(f"DMCA form submitted successfully to {contact.form_url}")
                                return True
                            else:
                                logger.warning(f"Form submission failed with status {response.status}")
                                return False
                else:
                    logger.warning("No form URL provided for platform contact")
                    return False
                    
            except Exception as e:
                logger.error(f"Form submission failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Erreur soumission formulaire DMCA: {e}")
            return False
    
    async def track_response(self, notice_id: str, response_data: Dict[str, Any]) -> bool:
        """Enregistre une réponse à une notification DMCA"""
        try:
            notice = self.active_notices.get(notice_id)
            if not notice:
                return False
            
            response_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': response_data.get('type', 'general'),
                'content': response_data.get('content', ''),
                'action_taken': response_data.get('action_taken', ''),
                'compliance_status': response_data.get('compliance_status', 'unknown')
            }
            
            notice.responses.append(response_entry)
            
            # Mise à jour du statut selon la réponse
            compliance_status = response_data.get('compliance_status', '').lower()
            if compliance_status == 'complied':
                notice.status = DMCAStatus.COMPLIED
            elif compliance_status == 'disputed':
                notice.status = DMCAStatus.DISPUTED
            elif compliance_status == 'acknowledged':
                notice.status = DMCAStatus.ACKNOWLEDGED
            
            logger.info(f"Réponse enregistrée pour notice {notice_id}: {compliance_status}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suivi réponse DMCA {notice_id}: {e}")
            return False
    
    async def escalate_notice(self, notice_id: str, reason: str = "No response") -> bool:
        """Escalade une notification DMCA"""
        try:
            notice = self.active_notices.get(notice_id)
            if not notice:
                return False
            
            # Création d'une notice d'escalation
            escalation_notice = await self.create_dmca_notice(
                infringement_evidence=InfringementEvidence(
                    original_url=notice.infringement_evidence['original_url'],
                    infringing_url=notice.infringement_evidence['infringing_url'],
                    similarity_score=notice.infringement_evidence['similarity_score'],
                    fingerprint_match=notice.infringement_evidence['fingerprint_match'],
                    timestamp_detected=datetime.fromisoformat(notice.infringement_evidence['detection_timestamp']),
                    screenshots=notice.infringement_evidence['screenshots'],
                    metadata={**notice.infringement_evidence['metadata'], 'escalation_reason': reason}
                ),
                copyright_owner=ContactInfo(**notice.copyright_owner),
                agent_contact=ContactInfo(**notice.agent_contact),
                platform=notice.platform,
                notice_type=NotificationType.ESCALATION
            )
            
            # Envoi de l'escalation
            success = await self.send_notice(escalation_notice.id, auto_send=True)
            
            if success:
                notice.status = DMCAStatus.ESCALATED
                logger.info(f"Notice {notice_id} escaladée: {escalation_notice.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur escalation notice {notice_id}: {e}")
            return False
    
    async def _monitor_responses(self):
        """Surveille les réponses aux notifications DMCA"""
        while self.running:
            try:
                for notice_id, notice in self.active_notices.items():
                    if notice.status == DMCAStatus.SENT and notice.response_deadline:
                        if datetime.utcnow() > notice.response_deadline:
                            logger.warning(f"Notice {notice_id} en retard de réponse")
                            # Implement automatic response verification
                            await self._check_notice_response(notice_id)
                            
                            # Update notice status if needed
                            notice = self.active_notices.get(notice_id)
                            if notice and notice.status == DMCAStatus.SENT:
                                # Mark as requiring manual follow-up after deadline
                                notice.status = DMCAStatus.REQUIRES_FOLLOWUP
                                logger.info(f"Notice {notice_id} marked for manual follow-up")
                
                await asyncio.sleep(3600)  # Vérification horaire
                
            except Exception as e:
                logger.error(f"Erreur monitoring réponses DMCA: {e}")
                await asyncio.sleep(3600)
    
    async def _auto_escalation_monitor(self):
        """Surveille et déclenche les escalations automatiques"""
        while self.running:
            try:
                escalation_days = self.config.get('escalation_days', 14)
                
                for notice_id, notice in self.active_notices.items():
                    if (notice.status == DMCAStatus.SENT and 
                        notice.response_deadline and
                        datetime.utcnow() > notice.response_deadline + timedelta(days=escalation_days)):
                        
                        logger.info(f"Escalation automatique pour notice {notice_id}")
                        await self.escalate_notice(notice_id, "Automatic escalation - no response")
                
                await asyncio.sleep(86400)  # Vérification quotidienne
                
            except Exception as e:
                logger.error(f"Erreur escalation automatique: {e}")
                await asyncio.sleep(86400)
    
    async def _load_active_notices(self):
        """Charge les notices actives depuis le stockage persistant"""
        try:
            # Implementation: Load from database/storage
            try:
                # Basic implementation - could be replaced with actual DB calls
                stored_notices_file = Path("./data/active_dmca_notices.json")
                if stored_notices_file.exists():
                    with open(stored_notices_file, 'r', encoding='utf-8') as f:
                        notices_data = json.load(f)
                        
                    for notice_data in notices_data:
                        notice = DMCANotice(**notice_data)
                        self.active_notices[notice.id] = notice
                        
                    logger.info(f"Loaded {len(self.active_notices)} active DMCA notices")
                else:
                    logger.info("No stored DMCA notices found")
                    
            except Exception as e:
                logger.error(f"Error loading DMCA notices: {e}")
                self.active_notices = {}
        except Exception as e:
            logger.error(f"Erreur chargement notices DMCA: {e}")
    
    def _generate_notice_id(self) -> str:
        """Génère un ID unique pour les notifications DMCA"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(4)
        return f"DMCA-{timestamp}-{random_suffix}"
    
    async def get_notice_status(self, notice_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut détaillé d'une notification"""
        try:
            notice = self.active_notices.get(notice_id)
            if not notice:
                return None
            
            return {
                'id': notice.id,
                'type': notice.type.value,
                'status': notice.status.value,
                'platform': notice.platform.value,
                'created_at': notice.created_at.isoformat(),
                'sent_at': notice.sent_at.isoformat() if notice.sent_at else None,
                'response_deadline': notice.response_deadline.isoformat() if notice.response_deadline else None,
                'responses_count': len(notice.responses),
                'infringement_url': notice.infringement_evidence['infringing_url'],
                'similarity_score': notice.infringement_evidence['similarity_score']
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération statut notice {notice_id}: {e}")
            return None
    
    async def generate_compliance_report(self, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Génère un rapport de conformité DMCA"""
        try:
            start_date, end_date = date_range
            
            filtered_notices = [
                notice for notice in self.active_notices.values()
                if start_date <= notice.created_at <= end_date
            ]
            
            # Statistiques par statut
            status_stats = {}
            for status in DMCAStatus:
                count = len([n for n in filtered_notices if n.status == status])
                status_stats[status.value] = count
            
            # Statistiques par plateforme
            platform_stats = {}
            for platform in PlatformType:
                notices = [n for n in filtered_notices if n.platform == platform]
                platform_stats[platform.value] = {
                    'total': len(notices),
                    'complied': len([n for n in notices if n.status == DMCAStatus.COMPLIED]),
                    'disputed': len([n for n in notices if n.status == DMCAStatus.DISPUTED]),
                    'pending': len([n for n in notices if n.status == DMCAStatus.PENDING])
                }
            
            # Temps de réponse moyens
            response_times = []
            for notice in filtered_notices:
                if notice.sent_at and notice.responses:
                    first_response = min(notice.responses, key=lambda r: r['timestamp'])
                    response_time = (datetime.fromisoformat(first_response['timestamp']) - notice.sent_at).days
                    response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_notices': len(filtered_notices),
                    'compliance_rate': (status_stats.get('complied', 0) / len(filtered_notices) * 100) if filtered_notices else 0,
                    'average_response_time_days': round(avg_response_time, 1),
                    'escalation_rate': (status_stats.get('escalated', 0) / len(filtered_notices) * 100) if filtered_notices else 0
                },
                'status_breakdown': status_stats,
                'platform_breakdown': platform_stats,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Rapport DMCA généré: {len(filtered_notices)} notices")
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport DMCA: {e}")
            return {}
    
    async def shutdown(self):
        """Arrêt propre du service DMCA"""
        try:
            logger.info("Arrêt du service DMCA...")
            self.running = False
            
            # Sauvegarde des notices actives
            await self._save_active_notices()
            
            # Fermeture du client email
            if self.email_client:
                await self.email_client.close()
            
            logger.info("Service DMCA arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt service DMCA: {e}")
    
    async def _save_active_notices(self):
        """Sauvegarde les notices actives"""
        try:
            # Implementation: Save to database/storage
            try:
                # Basic implementation - could be replaced with actual DB calls
                notices_data = []
                for notice in self.active_notices.values():
                    notice_dict = {
                        'id': notice.id,
                        'type': notice.type.value,
                        'content_id': notice.content_id,
                        'infringing_urls': notice.infringing_urls,
                        'status': notice.status.value,
                        'created_at': notice.created_at.isoformat(),
                        'response_deadline': notice.response_deadline.isoformat() if notice.response_deadline else None
                    }
                    notices_data.append(notice_dict)
                
                # Ensure data directory exists
                data_dir = Path("./data")
                data_dir.mkdir(exist_ok=True)
                
                # Save to file
                stored_notices_file = data_dir / "active_dmca_notices.json"
                with open(stored_notices_file, 'w', encoding='utf-8') as f:
                    json.dump(notices_data, f, indent=2)
                    
                logger.info(f"Saved {len(notices_data)} active DMCA notices to storage")
                
            except Exception as e:
                logger.error(f"Error saving DMCA notices: {e}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde notices DMCA: {e}")


# Service singleton
dmca_service = DMCAAutomationService()


async def get_dmca_service() -> DMCAAutomationService:
    """Récupère l'instance du service DMCA"""
    return dmca_service


__all__ = [
    'DMCAAutomationService',
    'DMCANotice',
    'DMCAStatus',
    'NotificationType',
    'PlatformType',
    'ContactInfo',
    'InfringementEvidence',
    'PlatformContact',
    'DMCATemplate',
    'get_dmca_service'
]
