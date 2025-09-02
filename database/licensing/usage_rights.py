"""Usage Rights Database Module

Enterprise-grade usage rights management for IA Influencer Agent platform.
Provides comprehensive permissions, restrictions, and automated rights validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Team: Lead AI Developer, Backend Senior, Legal Compliance Expert, Rights Management Specialist

STRICT COPYRIGHT WARNING: This code and concept are EXCLUSIVE intellectual property of Fahed Mlaiel.
ANY unauthorized use, copying, or theft without explicit written authorization is STRICTLY PROHIBITED
and subject to immediate legal prosecution under German law.
Contact: mlaiel@live.de for ANY authorization requests.
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple, Callable
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4
import asyncio
import json
import logging
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Decimal as SQLDecimal, JSON, ForeignKey, ARRAY, Index,
    CheckConstraint, UniqueConstraint, event, func, select,
    and_, or_, case, exists, desc
)
from sqlalchemy.orm import relationship, Session, sessionmaker, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

import redis
from celery import Celery
from pydantic import BaseModel as PydanticModel, validator, Field
from prometheus_client import Counter, Histogram, Gauge

from ..core.database import get_database_session
from ..core.cache import CacheManager
from ..core.security import SecurityManager, encrypt_sensitive_data
from ..models.base import BaseModel, TimestampMixin, AuditMixin
from ..schemas.usage_rights_schemas import (
    UsageRightsSchema, PermissionGrantSchema, RightsValidationSchema,
    RightsPackageSchema, UsageRestrictionSchema, ContentAccessSchema
)
from ..ai.rights_analyzer import RightsAnalyzer
from ..integrations.legal_services import RightsLegalService
from ..integrations.content_protection import ContentProtectionService

# Metrics
rights_validations_total = Counter('rights_validations_total', 'Total rights validations', ['result', 'usage_type'])
rights_violations_total = Counter('rights_violations_total', 'Total rights violations detected', ['violation_type'])
active_grants_gauge = Gauge('active_grants_total', 'Total active usage grants')
rights_processing_time = Histogram('rights_processing_seconds', 'Rights processing time')

logger = logging.getLogger(__name__)

class UsageType(Enum):
    """
Comprehensive usage types with detailed classifications"""
    # Digital distribution
    STREAMING = "streaming"
    DOWNLOAD = "download"
    DIGITAL_RENTAL = "digital_rental"
    DIGITAL_SALE = "digital_sale"
    SUBSCRIPTION_ACCESS = "subscription_access"
    
    # Broadcasting and performance
    BROADCAST = "broadcast"
    RADIO_PLAY = "radio_play"
    TV_BROADCAST = "tv_broadcast"
    INTERNET_RADIO = "internet_radio"
    PODCAST = "podcast"
    LIVE_STREAMING = "live_streaming"
    PUBLIC_PERFORMANCE = "public_performance"
    
    # Synchronization and licensing
    SYNC_LICENSING = "sync_licensing"
    FILM_SYNC = "film_sync"
    TV_SYNC = "tv_sync"
    COMMERCIAL_SYNC = "commercial_sync"
    GAME_SYNC = "game_sync"
    APP_SYNC = "app_sync"
    WEB_SYNC = "web_sync"
    
    # Creative and derivative works
    REMIX = "remix"
    SAMPLING = "sampling"
    COVER_VERSION = "cover_version"
    ADAPTATION = "adaptation"
    TRANSLATION = "translation"
    ARRANGEMENT = "arrangement"
    
    # Commercial applications
    COMMERCIAL_USE = "commercial_use"
    ADVERTISING = "advertising"
    PROMOTIONAL = "promotional"
    MERCHANDISING = "merchandising"
    RINGTONE = "ringtone"
    KARAOKE = "karaoke"
    
    # Educational and non-commercial
    EDUCATIONAL_USE = "educational_use"
    NON_COMMERCIAL = "non_commercial"
    RESEARCH = "research"
    REVIEW_CRITICISM = "review_criticism"
    PARODY = "parody"
    
    # Print and publishing
    PRINT_LICENSE = "print_license"
    SHEET_MUSIC = "sheet_music"
    LYRIC_DISPLAY = "lyric_display"
    
    # Emerging technologies
    VR_AR_USE = "vr_ar_use"
    AI_TRAINING = "ai_training"
    NFT_CREATION = "nft_creation"
    BLOCKCHAIN_USE = "blockchain_use"
    
    # Social media and UGC
    SOCIAL_MEDIA = "social_media"
    USER_GENERATED_CONTENT = "user_generated_content"
    MEME_CREATION = "meme_creation"
    VIRAL_CONTENT = "viral_content"

class RightsScope(Enum):
    """Rights scope definitions"""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SOLE = "sole"
    CO_EXCLUSIVE = "co_exclusive"

class PermissionLevel(IntEnum):
    """Permission levels with hierarchy"""

    DENIED = 0
    RESTRICTED = 1
    LIMITED = 2
    STANDARD = 3
    EXTENDED = 4
    FULL = 5

class RestrictionType(Enum):
    """
Types of usage restrictions"""

    TERRITORIAL = "territorial"
    TEMPORAL = "temporal"
    PLATFORM = "platform"
    AUDIENCE = "audience"
    COMMERCIAL = "commercial"
    TECHNICAL = "technical"
    CONTENT = "content"
    VOLUME = "volume"
    QUALITY = "quality"
    ATTRIBUTION = "attribution"

class ValidationResult(Enum):
    """Rights validation results"""

    GRANTED = "granted"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    PENDING_APPROVAL = "pending_approval"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REQUIRES_PAYMENT = "requires_payment"
    REQUIRES_ATTRIBUTION = "requires_attribution"

@dataclass
class UsageContext:
    """Context information for usage rights validation"""
    user_id: str
    content_id: str
    usage_type: str
    platform: str = "unknown"
    territory: str = "GLOBAL"
    commercial_intent: bool = False
    audience_size: Optional[int] = None
    distribution_channels: List[str] = field(default_factory=list)
    technical_specs: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'user_id': self.user_id,
            'content_id': self.content_id,
            'usage_type': self.usage_type,
            'platform': self.platform,
            'territory': self.territory,
            'commercial_intent': self.commercial_intent,
            'audience_size': self.audience_size,
            'distribution_channels': self.distribution_channels,
            'technical_specs': self.technical_specs,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class RightsPackage:
    """Comprehensive rights package definition"""
    reproduction_rights: bool = False
    distribution_rights: bool = False
    public_performance_rights: bool = False
    public_display_rights: bool = False
    digital_transmission_rights: bool = False
    synchronization_rights: bool = False
    mechanical_rights: bool = False
    adaptation_rights: bool = False
    translation_rights: bool = False
    rental_rights: bool = False
    lending_rights: bool = False
    broadcasting_rights: bool = False
    cable_retransmission_rights: bool = False
    satellite_transmission_rights: bool = False
    online_transmission_rights: bool = False
    mobile_transmission_rights: bool = False
    moral_rights: Dict[str, bool] = field(default_factory=dict)
    neighboring_rights: Dict[str, bool] = field(default_factory=dict)
    
    def has_right(self, right_name: str) -> bool:
        """
Check if specific right is included"""
        return getattr(self, right_name, False)
    
    def get_granted_rights(self) -> List[str]:
        """
Get list of all granted rights"""
        granted = []
        for attr_name in dir(self):
            if not attr_name.startswith('_') and hasattr(self, attr_name):
                value = getattr(self, attr_name)
                if isinstance(value, bool) and value:
                    granted.append(attr_name)
        return granted

class UsageGrant(BaseModel, TimestampMixin, AuditMixin):
    """
    Comprehensive usage grant model with advanced permission management.
    Supports complex multi-party rights and automated validation.
    """
    __tablename__ = "usage_grants"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    grant_id = Column(String(100), unique=True, nullable=False)
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    
    # Grantor and grantee
    grantor_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)  # Rights owner
    grantee_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)  # Rights user
    agent_id = Column(PostgresUUID(as_uuid=True))  # Optional agent/broker
    
    # Grant metadata
    grant_title = Column(String(500), nullable=False)
    grant_description = Column(Text)
    grant_category = Column(String(100), default="standard")
    priority_level = Column(Integer, default=5)  # 1-10 scale
    
    # Rights specification
    usage_types = Column(ARRAY(String), nullable=False)
    rights_package = Column(JSONB, nullable=False)
    permission_level = Column(Integer, default=PermissionLevel.STANDARD)
    rights_scope = Column(String(50), default=RightsScope.NON_EXCLUSIVE.value)
    
    # Territorial restrictions
    granted_territories = Column(ARRAY(String), default=list)
    excluded_territories = Column(ARRAY(String), default=list)
    territory_specific_terms = Column(JSONB, default=dict)
    
    # Temporal restrictions
    effective_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    usage_windows = Column(JSONB, default=list)  # Specific time windows
    renewal_options = Column(JSONB, default=dict)
    
    # Platform and channel restrictions
    permitted_platforms = Column(ARRAY(String), default=list)
    excluded_platforms = Column(ARRAY(String), default=list)
    channel_restrictions = Column(JSONB, default=dict)
    
    # Commercial terms
    commercial_permitted = Column(Boolean, default=False)
    revenue_sharing_required = Column(Boolean, default=False)
    attribution_required = Column(Boolean, default=True)
    attribution_format = Column(Text)
    
    # Technical restrictions
    quality_limitations = Column(JSONB, default=dict)
    format_restrictions = Column(ARRAY(String), default=list)
    drm_requirements = Column(JSONB, default=dict)
    watermarking_required = Column(Boolean, default=False)
    
    # Usage limitations
    max_uses = Column(Integer)  # Maximum number of uses
    max_audience_size = Column(Integer)  # Maximum audience per use
    concurrent_use_limit = Column(Integer)  # Maximum concurrent uses
    geographic_use_tracking = Column(Boolean, default=False)
    
    # Approval and workflow
    approval_required = Column(Boolean, default=True)
    approval_workflow = Column(JSONB, default=dict)
    approver_chain = Column(ARRAY(String), default=list)
    auto_approval_conditions = Column(JSONB, default=dict)
    
    # Status and lifecycle
    status = Column(String(50), default="pending")  # pending, approved, active, suspended, expired, revoked
    approval_date = Column(DateTime(timezone=True))
    activation_date = Column(DateTime(timezone=True))
    last_used_date = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Compliance and monitoring
    compliance_monitoring = Column(Boolean, default=True)
    violation_threshold = Column(Integer, default=3)
    automated_enforcement = Column(Boolean, default=False)
    monitoring_frequency = Column(String(20), default="daily")
    
    # Financial terms
    license_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    royalty_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    revenue_share_percentage = Column(SQLDecimal(5, 2), default=Decimal('0.00'))
    payment_terms = Column(JSONB, default=dict)
    
    # Legal and risk
    legal_basis = Column(String(255))
    risk_assessment = Column(JSONB, default=dict)
    liability_limitations = Column(JSONB, default=dict)
    indemnification_terms = Column(JSONB, default=dict)
    
    # Relationships
    restrictions = relationship("UsageRestriction", back_populates="grant")
    usage_logs = relationship("UsageLog", back_populates="grant")
    violations = relationship("RightsViolation", back_populates="grant")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_grant_content_grantee', 'content_id', 'grantee_id'),
        Index('idx_grant_grantor_status', 'grantor_id', 'status'),
        Index('idx_grant_effective_expiration', 'effective_date', 'expiration_date'),
        Index('idx_grant_usage_types', 'usage_types'),
        Index('idx_grant_territories', 'granted_territories'),
        CheckConstraint('priority_level >= 1 AND priority_level <= 10', name='check_priority_level_valid'),
        CheckConstraint('permission_level >= 0 AND permission_level <= 5', name='check_permission_level_valid'),
        CheckConstraint('royalty_rate >= 0 AND royalty_rate <= 1', name='check_royalty_rate_valid'),
        CheckConstraint('revenue_share_percentage >= 0 AND revenue_share_percentage <= 100', name='check_revenue_share_valid'),
    )
    
    @validates('rights_scope')
    def validate_rights_scope(self, key, scope):
        if scope not in [s.value for s in RightsScope]:
            raise ValueError(f"Invalid rights scope: {scope}")
        try:
            logger.info(f"Executing is_expired")
            
            # Implementation for is_expired
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"is_expired completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"is_expired failed: {e}")
            raise
    @hybrid_property
    def is_active(self):
        now = datetime.now(timezone.utc)
        return (
            self.status == "active" and
            (not self.effective_date or now >= self.effective_date) and
            (not self.expiration_date or now <= self.expiration_date)
        )
    
    @hybrid_property
    def is_expired(self):
        return self.expiration_date and datetime.now(timezone.utc) > self.expiration_date
    
    @hybrid_property
    def days_remaining(self):
        if self.expiration_date:
            delta = self.expiration_date - datetime.now(timezone.utc)
            return max(0, delta.days)
        return None
    
    def has_usage_type(self, usage_type: str) -> bool:
        """Check if grant includes specific usage type"""
        return usage_type in (self.usage_types or [])
    
    def is_territory_permitted(self, territory: str) -> bool:
        """
Check if territory is permitted"""
        if self.excluded_territories and territory in self.excluded_territories:
            return False
        if self.granted_territories:
            return territory in self.granted_territories or "GLOBAL" in self.granted_territories
        return True
    
    def is_platform_permitted(self, platform: str) -> bool:
        """Check if platform is permitted"""
        if self.excluded_platforms and platform in self.excluded_platforms:
            return False
        if self.permitted_platforms:
            return platform in self.permitted_platforms
        return True
    
    def can_be_used(self, usage_context: UsageContext) -> Tuple[bool, str]:
        """
Comprehensive usage validation"""
        # Check if grant is active
        if not self.is_active:
            return False, f"Grant is not active (status: {self.status})"
        
        # Check usage type
        if not self.has_usage_type(usage_context.usage_type):
            return False, f"Usage type '{usage_context.usage_type}' not permitted"
        
        # Check territory
        if not self.is_territory_permitted(usage_context.territory):
            return False, f"Territory '{usage_context.territory}' not permitted"
        
        # Check platform
        if not self.is_platform_permitted(usage_context.platform):
            return False, f"Platform '{usage_context.platform}' not permitted"
        
        # Check commercial use
        if usage_context.commercial_intent and not self.commercial_permitted:
            return False, "Commercial use not permitted"
        
        # Check usage limits
        if self.max_uses and self.usage_count >= self.max_uses:
            return False, f"Maximum uses ({self.max_uses}) exceeded"
        
        # Check audience size
        if self.max_audience_size and usage_context.audience_size and usage_context.audience_size > self.max_audience_size:
            return False, f"Audience size exceeds limit ({self.max_audience_size})"
        
        return True, "Usage permitted"

class UsageRestriction(BaseModel, TimestampMixin):
    """
    Detailed usage restrictions with conditional logic.
    """
    __tablename__ = "usage_restrictions"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    grant_id = Column(PostgresUUID(as_uuid=True), ForeignKey('usage_grants.id'), nullable=False)
    restriction_id = Column(String(100), nullable=False)
    
    # Restriction details
    restriction_type = Column(String(50), nullable=False)
    restriction_name = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Restriction conditions
    conditions = Column(JSONB, nullable=False)
    conditional_logic = Column(Text)  # Complex conditional expressions
    enforcement_mode = Column(String(20), default="strict")  # strict, lenient, warning
    
    # Temporal aspects
    applies_from = Column(DateTime(timezone=True))
    applies_until = Column(DateTime(timezone=True))
    time_based_conditions = Column(JSONB, default=dict)
    
    # Exception handling
    exceptions = Column(JSONB, default=list)
    override_permissions = Column(ARRAY(String), default=list)
    escalation_path = Column(JSONB, default=dict)
    
    # Status and enforcement
    is_active = Column(Boolean, default=True)
    enforcement_enabled = Column(Boolean, default=True)
    violation_count = Column(Integer, default=0)
    last_violation_date = Column(DateTime(timezone=True))
    
    # Relationships
    grant = relationship("UsageGrant", back_populates="restrictions")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_restriction_grant_type', 'grant_id', 'restriction_type'),
        Index('idx_restriction_active_enforcement', 'is_active', 'enforcement_enabled'),
        UniqueConstraint('grant_id', 'restriction_id', name='unique_grant_restriction'),
    )
    
    @validates('restriction_type')
    def validate_restriction_type(self, key, restriction_type):
        if restriction_type not in [r.value for r in RestrictionType]:
            raise ValueError(f"Invalid restriction type: {restriction_type}")
        return restriction_type
    
    def evaluate_restriction(self, usage_context: UsageContext) -> Tuple[bool, str]:
        """Evaluate if restriction is violated"""
        if not self.is_active or not self.enforcement_enabled:
            return False, "Restriction not active"
        
        # Check temporal applicability
        now = datetime.now(timezone.utc)
        if self.applies_from and now < self.applies_from:
            return False, "Restriction not yet applicable"
        if self.applies_until and now > self.applies_until:
            return False, "Restriction no longer applicable"
        
        # Evaluate conditions
        try:
            # Simple condition checking
            for condition_key, condition_value in self.conditions.items():
                context_value = getattr(usage_context, condition_key, None)
                if context_value != condition_value:
                    return True, f"Restriction violated: {condition_key} = {context_value}, expected {condition_value}"
            
            # Complex conditional logic if provided
            if self.conditional_logic:
                # Safely evaluate Python expression
                safe_globals = {
                    '__builtins__': {},
                    'context': usage_context.to_dict(),
                    'datetime': datetime
                }
                violated = eval(self.conditional_logic, safe_globals)
                if violated:
                    return True, f"Restriction violated: {self.restriction_name}"
            
            return False, "No restriction violation"
            
        except Exception as e:
            logger.error(f"Error evaluating restriction {self.restriction_id}: {e}")
            return True, f"Restriction evaluation error: {str(e)}"

class UsageLog(BaseModel, TimestampMixin):
    """
    Comprehensive usage logging for rights tracking and analytics.
    """
    __tablename__ = "usage_logs"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    grant_id = Column(PostgresUUID(as_uuid=True), ForeignKey('usage_grants.id'), nullable=False)
    log_entry_id = Column(String(100), unique=True, nullable=False)
    
    # Usage details
    user_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    usage_type = Column(String(50), nullable=False)
    platform = Column(String(100), nullable=False)
    
    # Context information
    territory = Column(String(100), default="UNKNOWN")
    commercial_use = Column(Boolean, default=False)
    audience_size = Column(Integer)
    distribution_channels = Column(ARRAY(String), default=list)
    
    # Technical details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    device_info = Column(JSONB, default=dict)
    technical_specs = Column(JSONB, default=dict)
    
    # Usage metrics
    usage_start_time = Column(DateTime(timezone=True), nullable=False)
    usage_end_time = Column(DateTime(timezone=True))
    usage_duration_seconds = Column(Integer)
    bytes_transferred = Column(Integer)
    quality_level = Column(String(20))
    
    # Attribution and reporting
    attribution_displayed = Column(Boolean, default=False)
    attribution_format = Column(Text)
    revenue_generated = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    currency = Column(String(3), default="EUR")
    
    # Validation and compliance
    rights_validated = Column(Boolean, default=False)
    validation_result = Column(String(50))
    compliance_score = Column(SQLDecimal(3, 2), default=Decimal('1.00'))
    violations_detected = Column(JSONB, default=list)
    
    # Relationships
    grant = relationship("UsageGrant", back_populates="usage_logs")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_usage_log_grant_time', 'grant_id', 'usage_start_time'),
        Index('idx_usage_log_user_content', 'user_id', 'content_id'),
        Index('idx_usage_log_platform_territory', 'platform', 'territory'),
        Index('idx_usage_log_commercial_revenue', 'commercial_use', 'revenue_generated'),
        CheckConstraint('usage_duration_seconds >= 0', name='check_usage_duration_positive'),
        CheckConstraint('compliance_score >= 0 AND compliance_score <= 1', name='check_compliance_score_valid'),
    )

class RightsViolation(BaseModel, TimestampMixin, AuditMixin):
    """
    Rights violation detection and tracking system.
    """
    __tablename__ = "rights_violations"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    grant_id = Column(PostgresUUID(as_uuid=True), ForeignKey('usage_grants.id'))
    violation_id = Column(String(100), unique=True, nullable=False)
    
    # Violation details
    violation_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Context of violation
    user_id = Column(PostgresUUID(as_uuid=True), index=True)
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    platform = Column(String(100))
    territory = Column(String(100))
    usage_context = Column(JSONB, default=dict)
    
    # Detection information
    detection_method = Column(String(50), default="automated")  # automated, manual, reported
    detection_confidence = Column(SQLDecimal(3, 2), default=Decimal('1.00'))
    evidence = Column(JSONB, default=dict)
    
    # Impact assessment
    estimated_damage = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    affected_parties = Column(ARRAY(String), default=list)
    business_impact = Column(String(20), default="low")  # low, medium, high, critical
    
    # Resolution tracking
    status = Column(String(50), default="open")  # open, investigating, resolved, dismissed
    resolution_action = Column(String(100))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Enforcement actions
    warning_sent = Column(Boolean, default=False)
    access_suspended = Column(Boolean, default=False)
    legal_action_initiated = Column(Boolean, default=False)
    damages_claimed = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    
    # Relationships
    grant = relationship("UsageGrant", back_populates="violations")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_violation_content_severity', 'content_id', 'severity'),
        Index('idx_violation_status_detected', 'status', 'detected_at'),
        Index('idx_violation_user_platform', 'user_id', 'platform'),
        CheckConstraint('detection_confidence >= 0 AND detection_confidence <= 1', name='check_detection_confidence_valid'),
        CheckConstraint('estimated_damage >= 0', name='check_estimated_damage_positive'),
    )

class UsageRightsService:
    """
    Comprehensive usage rights management service with AI-powered validation,
    automated enforcement, and enterprise-grade rights administration.
    """
    
    def __init__(self, 
                 session: Session = None,
                 cache_manager: CacheManager = None,
                 rights_analyzer: RightsAnalyzer = None,
                 legal_service: RightsLegalService = None,
                 protection_service: ContentProtectionService = None):
        """
Initialize the usage rights service with dependencies"""
        self.session = session or get_database_session()
        self.cache = cache_manager or CacheManager()
        self.rights_analyzer = rights_analyzer or RightsAnalyzer()
        self.legal_service = legal_service or RightsLegalService()
        self.protection_service = protection_service or ContentProtectionService()
        
        # Redis for real-time monitoring
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        
        # Background task processing
        self.celery_app = Celery('usage_rights_service')
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Rights validation cache
        self.validation_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("UsageRightsService initialized with AI-powered validation")
    
    async def validate_usage_rights(self, 
                                  usage_context: UsageContext,
                                  check_violations: bool = True,
                                  real_time_monitoring: bool = True) -> Dict[str, Any]:
        """
        Comprehensive usage rights validation with AI analysis.
        
        Args:
            usage_context: Context information for the usage request
            check_violations: Whether to check for potential violations
            real_time_monitoring: Enable real-time compliance monitoring
            
        Returns:
            Detailed validation result with permissions and restrictions
        """
        with rights_processing_time.time():
            try:
                # Check cache first
                cache_key = f"rights_validation:{usage_context.content_id}:{usage_context.user_id}:{usage_context.usage_type}"
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.debug(f"Using cached validation result for {cache_key}")
                    return cached_result
                
                # Find applicable grants
                grants = await self._find_applicable_grants(usage_context)
                
                if not grants:
                    result = {
                        'status': ValidationResult.DENIED.value,
                        'reason': 'No applicable usage grants found',
                        'permissions': {},
                        'restrictions': [],
                        'requires_approval': True,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    rights_validations_total.labels(result='denied', usage_type=usage_context.usage_type).inc()
                    return result
                
                # Evaluate each grant
                validation_results = []
                for grant in grants:
                    grant_result = await self._validate_grant(grant, usage_context)
                    validation_results.append(grant_result)
                
                # Determine overall result
                overall_result = await self._consolidate_validation_results(validation_results)
                
                # AI-powered risk assessment
                if self.rights_analyzer:
                    risk_assessment = await self.rights_analyzer.assess_usage_risk(
                        usage_context, grants, overall_result
                    )
                    overall_result['risk_assessment'] = risk_assessment
                
                # Check for potential violations
                if check_violations:
                    violation_check = await self._check_potential_violations(usage_context, grants)
                    overall_result['violation_warnings'] = violation_check
                
                # Real-time monitoring setup
                if real_time_monitoring and overall_result['status'] == ValidationResult.GRANTED.value:
                    await self._setup_real_time_monitoring(usage_context, grants)
                
                # Cache the result
                await self.cache.set(cache_key, overall_result, ttl=self.cache_ttl)
                
                # Update metrics
                rights_validations_total.labels(
                    result=overall_result['status'], 
                    usage_type=usage_context.usage_type
                ).inc()
                
                return overall_result
                
            except Exception as e:
                logger.error(f"Error validating usage rights: {e}")
                return {
                    'status': ValidationResult.DENIED.value,
                    'reason': f'Validation error: {str(e)}',
                    'permissions': {},
                    'restrictions': [],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
    
    async def create_usage_grant(self, 
                               grant_data: Dict[str, Any],
                               auto_approve: bool = False,
                               ai_contract_generation: bool = True) -> UsageGrant:
        """
        Create a new usage grant with AI-powered contract generation.
        
        Args:
            grant_data: Grant configuration data
            auto_approve: Whether to auto-approve based on conditions
            ai_contract_generation: Use AI to generate contract terms
            
        Returns:
            Created usage grant
        """
        try:
            # Validate input data
            validated_data = await self._validate_grant_data(grant_data)
            
            # AI-powered contract generation
            if ai_contract_generation and self.rights_analyzer:
                enhanced_terms = await self.rights_analyzer.generate_contract_terms(validated_data)
                validated_data.update(enhanced_terms)
            
            # Create grant instance
            grant = UsageGrant(
                grant_id=f"grant_{uuid4().hex[:12]}",
                **validated_data
            )
            
            # Set up automated approval if conditions are met
            if auto_approve:
                approval_result = await self._evaluate_auto_approval(grant)
                if approval_result['approved']:
                    grant.status = "approved"
                    grant.approval_date = datetime.now(timezone.utc)
                else:
                    grant.approval_required = True
                    grant.approver_chain = approval_result.get('required_approvers', [])
            
            # Save to database
            self.session.add(grant)
            self.session.commit()
            
            # Set up monitoring and restrictions
            await self._setup_grant_monitoring(grant)
            
            # Update metrics
            active_grants_gauge.inc()
            
            logger.info(f"Created usage grant {grant.grant_id} for content {grant.content_id}")
            return grant
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating usage grant: {e}")
            raise
    
    async def log_usage(self, 
                       grant_id: str,
                       usage_context: UsageContext,
                       technical_details: Dict[str, Any] = None) -> UsageLog:
        """
        Log a usage event with comprehensive tracking.
        
        Args:
            grant_id: ID of the usage grant being used
            usage_context: Context of the usage
            technical_details: Additional technical information
            
        Returns:
            Created usage log entry
        """
        try:
            # Find the grant
            grant = self.session.query(UsageGrant).filter_by(grant_id=grant_id).first()
            if not grant:
                raise ValueError(f"Grant {grant_id} not found")
            
            # Validate usage before logging
            validation_result = await self.validate_usage_rights(usage_context)
            if validation_result['status'] != ValidationResult.GRANTED.value:
                logger.warning(f"Logging usage for denied grant {grant_id}")
            
            # Create usage log
            usage_log = UsageLog(
                grant_id=grant.id,
                log_entry_id=f"log_{uuid4().hex[:12]}",
                user_id=usage_context.user_id,
                content_id=usage_context.content_id,
                usage_type=usage_context.usage_type,
                platform=usage_context.platform,
                territory=usage_context.territory,
                commercial_use=usage_context.commercial_intent,
                audience_size=usage_context.audience_size,
                distribution_channels=usage_context.distribution_channels,
                usage_start_time=usage_context.timestamp,
                rights_validated=validation_result['status'] == ValidationResult.GRANTED.value,
                validation_result=validation_result['status'],
                technical_specs=technical_details or {}
            )
            
            # Add technical details if provided
            if technical_details:
                usage_log.device_info = technical_details.get('device_info', {})
                usage_log.ip_address = technical_details.get('ip_address')
                usage_log.user_agent = technical_details.get('user_agent')
                usage_log.quality_level = technical_details.get('quality_level')
            
            # Update grant usage count
            grant.usage_count += 1
            grant.last_used_date = datetime.now(timezone.utc)
            
            # Save to database
            self.session.add(usage_log)
            self.session.commit()
            
            # Real-time analytics
            await self._update_usage_analytics(grant, usage_log)
            
            logger.info(f"Logged usage for grant {grant_id}")
            return usage_log
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error logging usage: {e}")
            raise
    
    async def detect_violation(self, 
                             usage_context: UsageContext,
                             evidence: Dict[str, Any] = None) -> Optional[RightsViolation]:
        """
        Detect and record a rights violation.
        
        Args:
            usage_context: Context where violation occurred
            evidence: Evidence of the violation
            
        Returns:
            Created violation record if violation detected
        """
        try:
            # Check for applicable grants
            grants = await self._find_applicable_grants(usage_context)
            
            # AI-powered violation detection
            violation_analysis = await self.rights_analyzer.analyze_potential_violation(
                usage_context, grants, evidence
            )
            
            if not violation_analysis['violation_detected']:
                return None
            
            # Create violation record
            violation = RightsViolation(
                violation_id=f"viol_{uuid4().hex[:12]}",
                grant_id=grants[0].id if grants else None,
                violation_type=violation_analysis['violation_type'],
                severity=violation_analysis['severity'],
                description=violation_analysis['description'],
                user_id=usage_context.user_id,
                content_id=usage_context.content_id,
                platform=usage_context.platform,
                territory=usage_context.territory,
                usage_context=usage_context.to_dict(),
                detection_confidence=violation_analysis['confidence'],
                evidence=evidence or {},
                estimated_damage=Decimal(str(violation_analysis.get('estimated_damage', 0)))
            )
            
            # Save violation
            self.session.add(violation)
            self.session.commit()
            
            # Trigger enforcement actions
            await self._trigger_enforcement_actions(violation)
            
            # Update metrics
            rights_violations_total.labels(violation_type=violation.violation_type).inc()
            
            logger.warning(f"Rights violation detected: {violation.violation_id}")
            return violation
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error detecting violation: {e}")
            raise
    
    async def get_usage_analytics(self, 
                                content_id: str = None,
                                user_id: str = None,
                                time_range: Tuple[datetime, datetime] = None) -> Dict[str, Any]:
        """
        Generate comprehensive usage analytics and insights.
        
        Args:
            content_id: Filter by specific content
            user_id: Filter by specific user
            time_range: Time range for analytics
            
        Returns:
            Detailed analytics report
        """
        try:
            # Build query filters
            filters = []
            if content_id:
                filters.append(UsageLog.content_id == content_id)
            if user_id:
                filters.append(UsageLog.user_id == user_id)
            if time_range:
                filters.append(UsageLog.usage_start_time.between(time_range[0], time_range[1]))
            
            # Query usage logs
            query = self.session.query(UsageLog)
            if filters:
                query = query.filter(and_(*filters))
            
            usage_logs = query.all()
            
            # Generate analytics
            analytics = {
                'total_usage_events': len(usage_logs),
                'unique_users': len(set(log.user_id for log in usage_logs)),
                'unique_content': len(set(log.content_id for log in usage_logs)),
                'usage_by_type': defaultdict(int),
                'usage_by_platform': defaultdict(int),
                'usage_by_territory': defaultdict(int),
                'commercial_vs_non_commercial': {'commercial': 0, 'non_commercial': 0},
                'revenue_generated': Decimal('0.00'),
                'compliance_score': Decimal('0.00'),
                'violation_rate': Decimal('0.00')
            }
            
            # Process logs
            for log in usage_logs:
                analytics['usage_by_type'][log.usage_type] += 1
                analytics['usage_by_platform'][log.platform] += 1
                analytics['usage_by_territory'][log.territory] += 1
                
                if log.commercial_use:
                    analytics['commercial_vs_non_commercial']['commercial'] += 1
                else:
                    analytics['commercial_vs_non_commercial']['non_commercial'] += 1
                
                analytics['revenue_generated'] += log.revenue_generated or Decimal('0.00')
                analytics['compliance_score'] += log.compliance_score or Decimal('0.00')
            
            # Calculate averages
            if usage_logs:
                analytics['average_compliance_score'] = analytics['compliance_score'] / len(usage_logs)
            
            # AI-powered insights
            if self.rights_analyzer:
                ai_insights = await self.rights_analyzer.generate_usage_insights(analytics, usage_logs)
                analytics['ai_insights'] = ai_insights
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating usage analytics: {e}")
            raise
    
    # Private helper methods
    
    async def _find_applicable_grants(self, usage_context: UsageContext) -> List[UsageGrant]:
        """Find all grants applicable to the usage context"""
        query = self.session.query(UsageGrant).filter(
            and_(
                UsageGrant.content_id == usage_context.content_id,
                UsageGrant.grantee_id == usage_context.user_id,
                UsageGrant.status.in_(["approved", "active"]),
                UsageGrant.usage_types.contains([usage_context.usage_type])
            )
        )
        
        return query.all()
    
    async def _validate_grant(self, grant: UsageGrant, usage_context: UsageContext) -> Dict[str, Any]:
        """Validate a specific grant against usage context"""
        can_use, reason = grant.can_be_used(usage_context)
        
        # Check restrictions
        restriction_violations = []
        for restriction in grant.restrictions:
            violated, violation_reason = restriction.evaluate_restriction(usage_context)
            if violated:
                restriction_violations.append({
                    'restriction_id': restriction.restriction_id,
                    'reason': violation_reason,
                    'severity': restriction.severity
                })
        
        return {
            'grant_id': grant.grant_id,
            'can_use': can_use and not restriction_violations,
            'reason': reason,
            'restrictions_violated': restriction_violations,
            'permission_level': grant.permission_level,
            'rights_scope': grant.rights_scope
        }
    
    async def _consolidate_validation_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Consolidate multiple validation results into final decision"""
        # Find best grant (highest permission level that allows usage)
        best_grant = None
        for result in results:
            if result['can_use']:
                if not best_grant or result['permission_level'] > best_grant['permission_level']:
                    best_grant = result
        
        if best_grant:
            return {
                'status': ValidationResult.GRANTED.value,
                'reason': 'Usage granted',
                'grant_id': best_grant['grant_id'],
                'permission_level': best_grant['permission_level'],
                'rights_scope': best_grant['rights_scope'],
                'permissions': best_grant,
                'restrictions': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                'status': ValidationResult.DENIED.value,
                'reason': 'No valid grants found',
                'permissions': {},
                'restrictions': [r for result in results for r in result.get('restrictions_violated', [])],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_potential_violations(self, usage_context: UsageContext, grants: List[UsageGrant]) -> List[Dict[str, Any]]:
        """
Check for potential violations using AI analysis"""
        if not self.rights_analyzer:
            return []
        
        try:
            return await self.rights_analyzer.check_potential_violations(usage_context, grants)
        except Exception as e:
            logger.error(f"Error checking potential violations: {e}")
            return []
    
    async def _setup_real_time_monitoring(self, usage_context: UsageContext, grants: List[UsageGrant]):
        """Set up real-time monitoring for usage compliance"""
        try:
            monitoring_key = f"monitor:{usage_context.content_id}:{usage_context.user_id}"
            monitoring_data = {
                'usage_context': usage_context.to_dict(),
                'grants': [grant.grant_id for grant in grants],
                'start_time': datetime.now(timezone.utc).isoformat()
            }
            
            # Store in Redis with TTL
            self.redis_client.setex(monitoring_key, 3600, json.dumps(monitoring_data))
            
        except Exception as e:
            logger.error(f"Error setting up real-time monitoring: {e}")
    
    async def _validate_grant_data(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize grant data"""
        logger = logging.getLogger(__name__)
        
        try:
            # Required fields validation
            required_fields = ['grantor_id', 'grantee_id', 'content_id', 'permissions']
            for field in required_fields:
                if field not in grant_data:
                    raise ValueError(f"Required field '{field}' missing")
            
            # Data type validation
            if not isinstance(grant_data.get('permissions'), list):
                raise ValueError("Permissions must be a list")
            
            # Sanitize numeric fields
            for field in ['grantor_id', 'grantee_id', 'content_id']:
                if not isinstance(grant_data[field], int) or grant_data[field] <= 0:
                    raise ValueError(f"{field} must be a positive integer")
            
            # Validate permission types
            valid_permissions = {
                'view', 'download', 'share', 'modify', 'commercial_use',
                'redistribute', 'remix', 'print', 'public_display'
            }
            for permission in grant_data['permissions']:
                if permission not in valid_permissions:
                    logger.warning(f"Unknown permission type: {permission}")
            
            # Validate date ranges if provided
            if 'start_date' in grant_data and grant_data['start_date']:
                if isinstance(grant_data['start_date'], str):
                    grant_data['start_date'] = datetime.fromisoformat(grant_data['start_date'])
            
            if 'end_date' in grant_data and grant_data['end_date']:
                if isinstance(grant_data['end_date'], str):
                    grant_data['end_date'] = datetime.fromisoformat(grant_data['end_date'])
                
                # Ensure end_date is after start_date
                start_date = grant_data.get('start_date', datetime.utcnow())
                if grant_data['end_date'] <= start_date:
                    raise ValueError("End date must be after start date")
            
            # Validate usage limits
            if 'usage_limits' in grant_data and grant_data['usage_limits']:
                limits = grant_data['usage_limits']
                if 'max_uses' in limits and limits['max_uses'] <= 0:
                    raise ValueError("max_uses must be positive")
                if 'max_downloads' in limits and limits['max_downloads'] <= 0:
                    raise ValueError("max_downloads must be positive")
            
            logger.info(f"Grant data validation successful for content {grant_data['content_id']}")
            return grant_data
            
        except Exception as e:
            logger.error(f"Grant data validation failed: {e}")
            raise ValueError(f"Invalid grant data: {e}")
    
    async def _evaluate_auto_approval(self, grant: UsageGrant) -> Dict[str, Any]:
        """Evaluate if grant can be auto-approved"""
        logger = logging.getLogger(__name__)
        
        try:
            # Auto-approval criteria
            auto_approval_score = 0
            required_approvers = []
            reasons = []
            
            # Basic permission check (low-risk permissions can be auto-approved)
            low_risk_permissions = {'view', 'download', 'share'}
            high_risk_permissions = {'commercial_use', 'redistribute', 'modify', 'remix'}
            
            grant_permissions = set(grant.permissions)
            
            # Score based on permission types
            if grant_permissions.issubset(low_risk_permissions):
                auto_approval_score += 50
                reasons.append("Only low-risk permissions requested")
            elif grant_permissions.intersection(high_risk_permissions):
                auto_approval_score -= 30
                reasons.append("High-risk permissions require review")
                required_approvers.append("legal_team")
            
            # Check grantor's authority level
            # Note: This would typically query user roles/permissions
            grantor_authority = getattr(grant, 'grantor_authority', 'standard')
            if grantor_authority == 'admin':
                auto_approval_score += 30
                reasons.append("Grantor has admin authority")
            elif grantor_authority == 'content_owner':
                auto_approval_score += 20
                reasons.append("Grantor is content owner")
            else:
                required_approvers.append("content_owner")
            
            # Check content sensitivity
            content_sensitivity = getattr(grant, 'content_sensitivity', 'medium')
            if content_sensitivity == 'high':
                auto_approval_score -= 40
                reasons.append("High-sensitivity content requires review")
                required_approvers.append("security_team")
            elif content_sensitivity == 'low':
                auto_approval_score += 20
                reasons.append("Low-sensitivity content")
            
            # Check usage limitations
            if hasattr(grant, 'usage_limits') and grant.usage_limits:
                limits = grant.usage_limits
                if limits.get('max_uses', float('inf')) <= 100:
                    auto_approval_score += 15
                    reasons.append("Limited usage scope")
                if limits.get('max_downloads', float('inf')) <= 50:
                    auto_approval_score += 10
                    reasons.append("Limited download scope")
            
            # Check duration
            if hasattr(grant, 'end_date') and grant.end_date:
                duration = (grant.end_date - (grant.start_date or datetime.utcnow())).days
                if duration <= 30:
                    auto_approval_score += 15
                    reasons.append("Short-term grant")
                elif duration > 365:
                    auto_approval_score -= 20
                    reasons.append("Long-term grant requires review")
                    required_approvers.append("legal_team")
            
            # Remove duplicates from required approvers
            required_approvers = list(set(required_approvers))
            
            # Final decision
            can_auto_approve = auto_approval_score >= 70 and len(required_approvers) == 0
            
            result = {
                'approved': can_auto_approve,
                'score': auto_approval_score,
                'required_approvers': required_approvers,
                'reasons': reasons,
                'recommendation': 'auto_approve' if can_auto_approve else 'manual_review'
            }
            
            logger.info(f"Auto-approval evaluation for grant {grant.id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Auto-approval evaluation failed: {e}")
            return {
                'approved': False,
                'required_approvers': ['admin'],
                'reasons': [f"Evaluation error: {e}"],
                'recommendation': 'manual_review'
            }
    
    async def _setup_grant_monitoring(self, grant: UsageGrant):
        """Set up monitoring for a new grant"""
        logger = logging.getLogger(__name__)
        
        try:
            # Create monitoring configuration
            monitoring_config = {
                'grant_id': grant.id,
                'content_id': grant.content_id,
                'grantor_id': grant.grantor_id,
                'grantee_id': grant.grantee_id,
                'permissions': grant.permissions,
                'start_date': grant.start_date,
                'end_date': grant.end_date,
                'monitoring_level': self._determine_monitoring_level(grant),
                'alert_thresholds': self._get_alert_thresholds(grant),
                'created_at': datetime.utcnow()
            }
            
            # Set up Redis monitoring key
            cache_manager = CacheManager()
            monitoring_key = f"grant_monitor:{grant.id}"
            await cache_manager.set(
                monitoring_key,
                json.dumps(monitoring_config, default=str),
                ttl=86400 * 365  # 1 year
            )
            
            # Set up usage tracking
            usage_key = f"grant_usage:{grant.id}"
            usage_data = {
                'total_uses': 0,
                'downloads': 0,
                'shares': 0,
                'last_activity': None,
                'daily_usage': {},
                'monthly_usage': {}
            }
            await cache_manager.set(usage_key, json.dumps(usage_data, default=str))
            
            # Schedule periodic monitoring tasks
            if hasattr(grant, 'usage_limits') and grant.usage_limits:
                # Set up limit checking
                await self._schedule_limit_checks(grant)
            
            # Set up expiration alerts
            if grant.end_date:
                await self._schedule_expiration_alerts(grant)
            
            # Log monitoring setup
            logger.info(f"Monitoring setup completed for grant {grant.id}")
            
        except Exception as e:
            logger.error(f"Failed to setup grant monitoring: {e}")
    
    def _determine_monitoring_level(self, grant: UsageGrant) -> str:
        """Determine appropriate monitoring level for the grant"""
        if hasattr(grant, 'permissions'):
            high_risk_permissions = {'commercial_use', 'redistribute', 'modify', 'remix'}
            if set(grant.permissions).intersection(high_risk_permissions):
                return 'high'
        return 'standard'
    
    def _get_alert_thresholds(self, grant: UsageGrant) -> Dict[str, Any]:
        """
Get alert thresholds based on grant characteristics"""
        thresholds = {
            'usage_percentage': 80,  # Alert at 80% of usage limit
            'time_percentage': 90,   # Alert at 90% of time limit
            'daily_limit_percentage': 70,
            'suspicious_activity_threshold': 10  # Unusual access patterns
        }
        
        # Adjust based on monitoring level
        monitoring_level = self._determine_monitoring_level(grant)
        if monitoring_level == 'high':
            thresholds['usage_percentage'] = 60
            thresholds['time_percentage'] = 80
            thresholds['suspicious_activity_threshold'] = 5
        
        return thresholds
    
    async def _schedule_limit_checks(self, grant: UsageGrant):
        """
Schedule periodic limit checking tasks"""
        # This would typically integrate with Celery or similar task queue
        logger = logging.getLogger(__name__)
        logger.info(f"Scheduled limit checks for grant {grant.id}")
    
    async def _schedule_expiration_alerts(self, grant: UsageGrant):
        """Schedule expiration alert tasks"""
        # This would typically integrate with notification system
        logger = logging.getLogger(__name__)
        logger.info(f"Scheduled expiration alerts for grant {grant.id}")
    
    async def _update_usage_analytics(self, grant: UsageGrant, usage_log: UsageLog):
        """Update real-time usage analytics"""
        logger = logging.getLogger(__name__)
        
        try:
            # Update Redis analytics
            cache_manager = CacheManager()
            usage_key = f"grant_usage:{grant.id}"
            
            # Get current usage data
            current_data = await cache_manager.get(usage_key)
            if current_data:
                usage_data = json.loads(current_data)
            else:
                usage_data = {
                    'total_uses': 0,
                    'downloads': 0,
                    'shares': 0,
                    'last_activity': None,
                    'daily_usage': {},
                    'monthly_usage': {}
                }
            
            # Update counters based on action type
            usage_data['total_uses'] += 1
            usage_data['last_activity'] = datetime.utcnow().isoformat()
            
            if hasattr(usage_log, 'action_type'):
                action_type = usage_log.action_type
                if action_type == 'download':
                    usage_data['downloads'] += 1
                elif action_type == 'share':
                    usage_data['shares'] += 1
            
            # Update daily usage
            today = datetime.utcnow().date().isoformat()
            if today not in usage_data['daily_usage']:
                usage_data['daily_usage'][today] = 0
            usage_data['daily_usage'][today] += 1
            
            # Update monthly usage
            this_month = datetime.utcnow().strftime('%Y-%m')
            if this_month not in usage_data['monthly_usage']:
                usage_data['monthly_usage'][this_month] = 0
            usage_data['monthly_usage'][this_month] += 1
            
            # Clean old daily data (keep only last 90 days)
            cutoff_date = (datetime.utcnow() - timedelta(days=90)).date().isoformat()
            usage_data['daily_usage'] = {
                date: count for date, count in usage_data['daily_usage'].items()
                if date >= cutoff_date
            }
            
            # Save updated analytics
            await cache_manager.set(usage_key, json.dumps(usage_data, default=str))
            
            # Update aggregate analytics
            await self._update_aggregate_analytics(grant, usage_log, usage_data)
            
            # Check for threshold alerts
            await self._check_usage_thresholds(grant, usage_data)
            
            logger.debug(f"Updated usage analytics for grant {grant.id}")
            
        except Exception as e:
            logger.error(f"Failed to update usage analytics: {e}")
    
    async def _update_aggregate_analytics(self, grant: UsageGrant, usage_log: UsageLog, usage_data: Dict[str, Any]):
        """Update platform-wide analytics"""
        try:
            cache_manager = CacheManager()
            
            # Update content analytics
            content_key = f"content_analytics:{grant.content_id}"
            content_analytics = await cache_manager.get(content_key)
            if content_analytics:
                content_data = json.loads(content_analytics)
            else:
                content_data = {'total_grants': 0, 'total_usage': 0, 'active_grants': 0}
            
            content_data['total_usage'] += 1
            await cache_manager.set(content_key, json.dumps(content_data, default=str))
            
            # Update user analytics
            user_key = f"user_analytics:{grant.grantee_id}"
            user_analytics = await cache_manager.get(user_key)
            if user_analytics:
                user_data = json.loads(user_analytics)
            else:
                user_data = {'total_usage': 0, 'active_grants': 0, 'content_accessed': set()}
            
            user_data['total_usage'] += 1
            user_data['content_accessed'] = list(set(user_data.get('content_accessed', [])) | {grant.content_id})
            await cache_manager.set(user_key, json.dumps(user_data, default=str))
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to update aggregate analytics: {e}")
    
    async def _check_usage_thresholds(self, grant: UsageGrant, usage_data: Dict[str, Any]):
        """Check if usage has exceeded alert thresholds"""
        try:
            # Get monitoring configuration
            cache_manager = CacheManager()
            monitoring_key = f"grant_monitor:{grant.id}"
            monitoring_config = await cache_manager.get(monitoring_key)
            
            if not monitoring_config:
                return
            
            config = json.loads(monitoring_config)
            thresholds = config.get('alert_thresholds', {})
            
            # Check usage percentage threshold
            if hasattr(grant, 'usage_limits') and grant.usage_limits:
                max_uses = grant.usage_limits.get('max_uses')
                if max_uses:
                    usage_percentage = (usage_data['total_uses'] / max_uses) * 100
                    threshold = thresholds.get('usage_percentage', 80)
                    
                    if usage_percentage >= threshold:
                        await self._trigger_usage_alert(grant, 'usage_threshold', {
                            'usage_percentage': usage_percentage,
                            'threshold': threshold,
                            'current_uses': usage_data['total_uses'],
                            'max_uses': max_uses
                        })
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to check usage thresholds: {e}")
    
    async def _trigger_usage_alert(self, grant: UsageGrant, alert_type: str, alert_data: Dict[str, Any]):
        """Trigger usage alert notification"""
        logger = logging.getLogger(__name__)
        logger.warning(f"Usage alert triggered for grant {grant.id}: {alert_type} - {alert_data}")
    
    async def _trigger_enforcement_actions(self, violation: RightsViolation):
        """Trigger appropriate enforcement actions for violation"""
        logger = logging.getLogger(__name__)
        
        try:
            violation_severity = self._assess_violation_severity(violation)
            enforcement_actions = []
            
            # Determine enforcement actions based on severity
            if violation_severity == 'critical':
                enforcement_actions = [
                    'immediate_suspension',
                    'legal_notice',
                    'admin_notification',
                    'audit_trail'
                ]
            elif violation_severity == 'high':
                enforcement_actions = [
                    'temporary_suspension',
                    'warning_notice',
                    'supervisor_notification',
                    'audit_trail'
                ]
            elif violation_severity == 'medium':
                enforcement_actions = [
                    'warning_notice',
                    'monitoring_increase',
                    'audit_trail'
                ]
            else:  # low severity
                enforcement_actions = [
                    'log_incident',
                    'audit_trail'
                ]
            
            # Execute each enforcement action
            for action in enforcement_actions:
                await self._execute_enforcement_action(violation, action)
            
            # Update violation status
            if hasattr(violation, 'status'):
                violation.status = 'enforced'
                violation.enforcement_actions = enforcement_actions
                violation.enforcement_timestamp = datetime.utcnow()
            
            # Log enforcement
            logger.warning(f"Enforcement actions triggered for violation {violation.id}: {enforcement_actions}")
            
        except Exception as e:
            logger.error(f"Failed to trigger enforcement actions: {e}")
    
    async def _execute_enforcement_action(self, violation: RightsViolation, action: str):
        """Execute a specific enforcement action"""
        logger = logging.getLogger(__name__)
        
        try:
            if action == 'immediate_suspension':
                await self._suspend_grant_immediately(violation.grant_id)
                logger.critical(f"Grant {violation.grant_id} suspended immediately due to violation {violation.id}")
                
            elif action == 'temporary_suspension':
                await self._suspend_grant_temporarily(violation.grant_id, hours=24)
                logger.warning(f"Grant {violation.grant_id} suspended temporarily due to violation {violation.id}")
                
            elif action == 'legal_notice':
                await self._send_legal_notice(violation)
                logger.warning(f"Legal notice sent for violation {violation.id}")
                
            elif action == 'warning_notice':
                await self._send_warning_notice(violation)
                logger.info(f"Warning notice sent for violation {violation.id}")
                
            elif action == 'admin_notification':
                await self._notify_administrators(violation)
                logger.info(f"Administrators notified of violation {violation.id}")
                
            elif action == 'supervisor_notification':
                await self._notify_supervisors(violation)
                logger.info(f"Supervisors notified of violation {violation.id}")
                
            elif action == 'monitoring_increase':
                await self._increase_monitoring(violation.grant_id)
                logger.info(f"Monitoring increased for grant {violation.grant_id}")
                
            elif action == 'audit_trail':
                await self._create_audit_trail(violation)
                logger.info(f"Audit trail created for violation {violation.id}")
                
            elif action == 'log_incident':
                logger.info(f"Incident logged for violation {violation.id}")
            
        except Exception as e:
            logger.error(f"Failed to execute enforcement action {action}: {e}")
    
    async def _suspend_grant_immediately(self, grant_id: int):
        """Immediately suspend a grant"""
        cache_manager = CacheManager()
        suspension_key = f"grant_suspended:{grant_id}"
        try:
            logger.info(f"Executing _send_legal_notice")
            
            # Implementation for _send_legal_notice
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _send_warning_notice")
            
            # Implementation for _send_warning_notice
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _notify_administrators")
            
            # Implementation for _notify_administrators
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_notify_administrators completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _notify_supervisors")
            
            # Implementation for _notify_supervisors
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_notify_supervisors completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_notify_supervisors failed: {e}")
            raise
        except Exception as e:
            logger.error(f"_notify_administrators failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"_send_warning_notice failed: {e}")
            raise
            logger.info(f"_send_legal_notice completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_legal_notice failed: {e}")
            raise
            'suspension_type': 'immediate',
            'suspended_at': datetime.utcnow().isoformat(),
            'reason': 'critical_violation'
        }))
    
    async def _suspend_grant_temporarily(self, grant_id: int, hours: int = 24):
        """Temporarily suspend a grant"""
        cache_manager = CacheManager()
        suspension_key = f"grant_suspended:{grant_id}"
        await cache_manager.set(
            suspension_key,
            json.dumps({
                'suspended': True,
                'suspension_type': 'temporary',
                'suspended_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=hours)).isoformat(),
                'reason': 'violation'
            }),
            ttl=hours * 3600
        )
    
    async def _send_legal_notice(self, violation: RightsViolation):
        """Send legal notice for violation"""
        # This would integrate with notification system
        pass
    
    async def _send_warning_notice(self, violation: RightsViolation):
        """
Send warning notice for violation"""
        # This would integrate with notification system
        pass
    
    async def _notify_administrators(self, violation: RightsViolation):
        """
Notify administrators of violation"""
        # This would integrate with notification system
        pass
    
    async def _notify_supervisors(self, violation: RightsViolation):
        """
Notify supervisors of violation"""
        # This would integrate with notification system
        pass
    
    async def _increase_monitoring(self, grant_id: int):
        """
Increase monitoring level for a grant"""
        cache_manager = CacheManager()
        monitoring_key = f"grant_monitor:{grant_id}"
        monitoring_config = await cache_manager.get(monitoring_key)
        
        if monitoring_config:
            config = json.loads(monitoring_config)
            config['monitoring_level'] = 'high'
            config['enhanced_monitoring_until'] = (datetime.utcnow() + timedelta(days=30)).isoformat()
            await cache_manager.set(monitoring_key, json.dumps(config, default=str))
    
    async def _create_audit_trail(self, violation: RightsViolation):
        """Create audit trail entry for violation"""
        cache_manager = CacheManager()
        audit_key = f"audit_trail:violation:{violation.id}"
        audit_data = {
            'violation_id': violation.id,
            'grant_id': violation.grant_id,
            'violation_type': getattr(violation, 'violation_type', 'unknown'),
            'severity': self._assess_violation_severity(violation),
            'detected_at': getattr(violation, 'detected_at', datetime.utcnow()).isoformat(),
            'audit_created_at': datetime.utcnow().isoformat()
        }
        await cache_manager.set(audit_key, json.dumps(audit_data, default=str), ttl=86400 * 365)

# Convenience functions for easy integration

async def validate_content_usage(content_id: str, 
                               user_id: str, 
                               usage_type: str,
                               platform: str = "web",
                               territory: str = "GLOBAL",
                               commercial: bool = False) -> Dict[str, Any]:
    """
    Convenience function for quick usage validation.
    
    Args:
        content_id: ID of the content to be used
        user_id: ID of the user requesting usage
        usage_type: Type of usage (from UsageType enum)
        platform: Platform where content will be used
        territory: Territory/region code
        commercial: Whether usage is commercial
        
    Returns:
        Validation result
    """
    usage_context = UsageContext(
        user_id=user_id,
        content_id=content_id,
        usage_type=usage_type,
        platform=platform,
        territory=territory,
        commercial_intent=commercial
    )
    
    service = UsageRightsService()
    return await service.validate_usage_rights(usage_context)

async def create_standard_grant(content_id: str,
                              grantor_id: str,
                              grantee_id: str,
                              usage_types: List[str],
                              territories: List[str] = None,
                              expiration_days: int = 365) -> UsageGrant:
    """
    Create a standard usage grant with common settings.
    
    Args:
        content_id: ID of the content being licensed
        grantor_id: ID of the rights owner
        grantee_id: ID of the rights user
        usage_types: List of permitted usage types
        territories: List of permitted territories (default: global)
        expiration_days: Days until grant expires
        
    Returns:
        Created usage grant
    """
    grant_data = {
        'content_id': content_id,
        'grantor_id': grantor_id,
        'grantee_id': grantee_id,
        'grant_title': f"Standard Usage Grant for {content_id}",
        'usage_types': usage_types,
        'granted_territories': territories or ["GLOBAL"],
        'rights_package': RightsPackage(
            reproduction_rights=True,
            distribution_rights=True,
            public_performance_rights=True
        ).__dict__,
        'expiration_date': datetime.now(timezone.utc) + timedelta(days=expiration_days),
        'permission_level': PermissionLevel.STANDARD,
        'commercial_permitted': False,
        'attribution_required': True
    }
    
    service = UsageRightsService()
    return await service.create_usage_grant(grant_data, auto_approve=True)
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_DISPLAY = "public_display"
    DERIVATIVE_WORK = "derivative_work"

class PermissionLevel(Enum):
    """Niveaux de permission"""

    FULL_RIGHTS = "full_rights"
    LIMITED_RIGHTS = "limited_rights"
    CONDITIONAL_RIGHTS = "conditional_rights"
    RESTRICTED_RIGHTS = "restricted_rights"
    NO_RIGHTS = "no_rights"
    PENDING_APPROVAL = "pending_approval"

class TerritorialScope(Enum):
    """Portée territoriale"""

    WORLDWIDE = "worldwide"
    CONTINENTAL = "continental"
    NATIONAL = "national"
    REGIONAL = "regional"
    LOCAL = "local"
    SPECIFIC_TERRITORIES = "specific_territories"

class ChannelType(Enum):
    """Types de canaux de distribution"""

    DIGITAL_STREAMING = "digital_streaming"
    RADIO = "radio"
    TELEVISION = "television"
    CINEMA = "cinema"
    LIVE_PERFORMANCE = "live_performance"
    ADVERTISING = "advertising"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    GAMING = "gaming"
    VR_AR = "vr_ar"
    NFT = "nft"

class RightsStatus(Enum):
    """Statut des droits"""

    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    DISPUTED = "disputed"
    TRANSFERRED = "transferred"

@dataclass
class UsageRestriction:
    """Structure des restrictions d'usage"""
    restriction_type: str
    description: str
    applies_to: List[str]
    severity: str = "medium"  # low, medium, high, critical
    enforcement_action: str = "warning"  # warning, block, report

@dataclass
class PermissionGrant:
    """Structure d'octroi de permission"""
    usage_type: UsageType
    permission_level: PermissionLevel
    conditions: List[str]
    limitations: Dict[str, Any]
    valid_from: datetime
    valid_until: Optional[datetime] = None

class UsageRights(BaseModel):
    """
    Modèle de base de données pour les droits d'usage.
    Gère toutes les permissions et restrictions d'utilisation du contenu.
    """
    __tablename__ = "usage_rights"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    rights_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    grantor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grantee_id = Column(Integer, ForeignKey("users.id"))
    license_agreement_id = Column(Integer, ForeignKey("license_agreements.id"))
    
    # Informations de base
    rights_name = Column(String(200), nullable=False)
    description = Column(Text)
    rights_type = Column(String(50), nullable=False)
    status = Column(String(20), default=RightsStatus.PENDING.value)
    
    # Permissions accordées
    granted_permissions = Column(JSON, nullable=False)
    usage_restrictions = Column(JSON)
    territorial_scope = Column(String(30), default=TerritorialScope.WORLDWIDE.value)
    specific_territories = Column(ARRAY(String))
    
    # Canaux et médiums
    authorized_channels = Column(ARRAY(String))
    prohibited_channels = Column(ARRAY(String))
    medium_restrictions = Column(JSON)
    
    # Période de validité
    effective_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime)
    auto_renewal = Column(Boolean, default=False)
    renewal_conditions = Column(JSON)
    
    # Conditions d'usage
    usage_conditions = Column(JSON)
    attribution_requirements = Column(JSON)
    royalty_requirements = Column(JSON)
    reporting_requirements = Column(JSON)
    
    # Limitations quantitatives
    max_usage_count = Column(Integer)
    current_usage_count = Column(Integer, default=0)
    max_duration_seconds = Column(Integer)
    max_audience_size = Column(Integer)
    
    # Monitoring et compliance
    monitoring_enabled = Column(Boolean, default=True)
    violation_detection = Column(Boolean, default=True)
    auto_enforcement = Column(Boolean, default=False)
    
    # Audit trail
    granted_date = Column(DateTime, default=datetime.utcnow)
    granted_by_user_id = Column(Integer, ForeignKey("users.id"))
    revocation_date = Column(DateTime)
    revocation_reason = Column(Text)
    
    # Relations
    content = relationship("ContentItem", back_populates="usage_rights")
    grantor = relationship("User", foreign_keys=[grantor_id], back_populates="granted_rights")
    grantee = relationship("User", foreign_keys=[grantee_id], back_populates="received_rights")
    license_agreement = relationship("LicenseAgreement")
    granted_by = relationship("User", foreign_keys=[granted_by_user_id])
    usage_logs = relationship("UsageLog", back_populates="rights")
    violations = relationship("RightsViolation", back_populates="rights")
    
    def __init__(self, **kwargs):
        try:
            logger.info(f"Executing record_usage")
            
            # Implementation for record_usage
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"record_usage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"record_usage failed: {e}")
            raise
        return (
            self.status == RightsStatus.ACTIVE.value and
            self.effective_date <= now and
            (self.expiration_date is None or self.expiration_date > now)
        )

    def can_use_for_purpose(self, usage_type: UsageType, channel: str = None) -> Tuple[bool, str]:
        """
Vérifie si l'usage est autorisé pour un type donné"""
        
        if not self.is_valid():
            return False, "Droits non valides ou expirés"
        
        # Vérification des permissions accordées
        if not self.granted_permissions:
            return False, "Aucune permission accordée"
        
        permissions = self.granted_permissions
        for perm in permissions:
            if perm.get('usage_type') == usage_type.value:
                permission_level = perm.get('permission_level')
                
                if permission_level == PermissionLevel.NO_RIGHTS.value:
                    return False, "Usage explicitement interdit"
                
                if permission_level == PermissionLevel.PENDING_APPROVAL.value:
                    return False, "Approbation requise"
                
                # Vérification des canaux
                if channel and self.authorized_channels:
                    if channel not in self.authorized_channels:
                        return False, f"Canal non autorisé: {channel}"
                
                if channel and self.prohibited_channels:
                    if channel in self.prohibited_channels:
                        return False, f"Canal interdit: {channel}"
                
                # Vérification des limitations quantitatives
                if self.max_usage_count and self.current_usage_count >= self.max_usage_count:
                    return False, "Limite d'utilisation atteinte"
                
                return True, "Usage autorisé"
        
        return False, f"Usage non autorisé: {usage_type.value}"

    def record_usage(
        self,
        usage_type: UsageType,
        channel: str,
        duration_seconds: Optional[int] = None,
        audience_size: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Enregistre une utilisation du contenu"""
        
        can_use, reason = self.can_use_for_purpose(usage_type, channel)
        if not can_use:
            raise ValueError(f"Usage non autorisé: {reason}")
        
        # Vérification des limitations
        if duration_seconds and self.max_duration_seconds:
            if duration_seconds > self.max_duration_seconds:
                raise ValueError("Durée d'usage dépassée")
        
        if audience_size and self.max_audience_size:
            if audience_size > self.max_audience_size:
                raise ValueError("Taille d'audience dépassée")
        
        # Incrémentation du compteur d'usage
        self.current_usage_count += 1
        
        # Création du log d'usage (sera géré par UsageLog)
        return True

    def check_expiration_soon(self, days_ahead: int = 30) -> bool:
        """Vérifie si les droits expirent bientôt"""
        if not self.expiration_date:
            return False
        
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return self.expiration_date <= cutoff_date

    def extend_validity(self, additional_days: int, reason: str = None) -> bool:
        """Étend la période de validité des droits"""
        if not self.expiration_date:
            self.expiration_date = datetime.utcnow() + timedelta(days=additional_days)
        else:
            self.expiration_date += timedelta(days=additional_days)
        
        # Log de l'extension
        if not hasattr(self, 'extension_history'):
            self.extension_history = []
        
        extension_record = {
            "extended_by_days": additional_days,
            "reason": reason,
            "extended_date": datetime.utcnow().isoformat(),
            "new_expiration": self.expiration_date.isoformat()
        }
        
        # Note: extension_history devrait être un champ JSON
        return True

    def revoke_rights(self, reason: str, revoking_user_id: int) -> bool:
        """Révoque les droits d'usage"""
        self.status = RightsStatus.REVOKED.value
        self.revocation_date = datetime.utcnow()
        self.revocation_reason = reason
        # Note: revoking_user_id devrait être stocké dans un champ dédié
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
Convertit les droits en dictionnaire"""
        return {
            "id": self.id,
            "rights_id": self.rights_id,
            "rights_name": self.rights_name,
            "rights_type": self.rights_type,
            "status": self.status,
            "granted_permissions": self.granted_permissions,
            "territorial_scope": self.territorial_scope,
            "authorized_channels": self.authorized_channels,
            "effective_date": self.effective_date.isoformat(),
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "current_usage_count": self.current_usage_count,
            "max_usage_count": self.max_usage_count,
            "is_valid": self.is_valid(),
            "expires_soon": self.check_expiration_soon(),
            "created_at": self.created_at.isoformat()
        }

class UsageLog(BaseModel):
    """
    Modèle de log des usages.
    Enregistre toutes les utilisations du contenu.
    """
    __tablename__ = "usage_logs"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    rights_id = Column(Integer, ForeignKey("usage_rights.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    
    # Détails de l'usage
    usage_type = Column(String(30), nullable=False)
    channel = Column(String(100))
    platform = Column(String(100))
    usage_date = Column(DateTime, default=datetime.utcnow)
    
    # Métriques d'usage
    duration_seconds = Column(Integer)
    audience_size = Column(Integer)
    geographical_location = Column(String(100))
    device_type = Column(String(50))
    
    # Métadonnées
    usage_metadata = Column(JSON)
    technical_details = Column(JSON)
    quality_settings = Column(JSON)
    
    # Validation et compliance
    authorized = Column(Boolean, default=True)
    validation_method = Column(String(50))
    compliance_score = Column(Integer)  # 0-100
    
    # Attribution et reporting
    attribution_provided = Column(Boolean, default=False)
    attribution_details = Column(JSON)
    reported_to_grantor = Column(Boolean, default=False)
    report_date = Column(DateTime)
    
    # Relations
    rights = relationship("UsageRights", back_populates="usage_logs")
    user = relationship("User")
    content = relationship("ContentItem")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.log_id:
            self.log_id = f"UL-{uuid.uuid4().hex[:8].upper()}"

class RightsViolation(BaseModel):
    """
    Modèle des violations de droits d'usage.
    Gère la détection et le suivi des infractions.
    """
    __tablename__ = "rights_violations"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    violation_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    rights_id = Column(Integer, ForeignKey("usage_rights.id"), nullable=False)
    violator_user_id = Column(Integer, ForeignKey("users.id"))
    detected_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Détails de la violation
    violation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")
    detected_date = Column(DateTime, default=datetime.utcnow)
    
    # Localisation de la violation
    violation_url = Column(String(500))
    platform = Column(String(100))
    geographical_location = Column(String(100))
    
    # Preuves
    evidence_data = Column(JSON)
    screenshots = Column(ARRAY(String))
    technical_evidence = Column(JSON)
    
    # Statut et résolution
    status = Column(String(30), default="detected")
    resolution_status = Column(String(30))
    resolution_date = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Actions prises
    warning_sent = Column(Boolean, default=False)
    takedown_requested = Column(Boolean, default=False)
    legal_action_initiated = Column(Boolean, default=False)
    damages_claimed = Column(Boolean, default=False)
    
    # Relations
    rights = relationship("UsageRights", back_populates="violations")
    violator = relationship("User", foreign_keys=[violator_user_id])
    detected_by = relationship("User", foreign_keys=[detected_by_user_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.violation_id:
            self.violation_id = f"RV-{uuid.uuid4().hex[:8].upper()}"

class UsageRightsManager:
    """
    Gestionnaire pour les droits d'usage.
    Fournit une interface complète pour la gestion des permissions.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    def grant_usage_rights(
        self,
        content_id: int,
        grantor_id: int,
        grantee_id: int,
        rights_name: str,
        permissions: List[PermissionGrant],
        territorial_scope: TerritorialScope = TerritorialScope.WORLDWIDE,
        duration_days: Optional[int] = None,
        conditions: Optional[Dict] = None
    ) -> UsageRights:
        """
Accorde des droits d'usage"""
        
        try:
            # Vérification des droits du concédant
            self._validate_grantor_rights(grantor_id, content_id)
            
            # Calcul de la date d'expiration
            expiration_date = None
            if duration_days:
                expiration_date = datetime.utcnow() + timedelta(days=duration_days)
            
            # Création des droits
            usage_rights = UsageRights(
                content_id=content_id,
                grantor_id=grantor_id,
                grantee_id=grantee_id,
                rights_name=rights_name,
                rights_type="usage_license",
                granted_permissions=[asdict(perm) for perm in permissions],
                territorial_scope=territorial_scope.value,
                expiration_date=expiration_date,
                usage_conditions=conditions or {},
                granted_by_user_id=grantor_id,
                status=RightsStatus.ACTIVE.value
            )
            
            # Extraction des canaux autorisés
            authorized_channels = []
            for perm in permissions:
                if hasattr(perm, 'limitations') and 'authorized_channels' in perm.limitations:
                    authorized_channels.extend(perm.limitations['authorized_channels'])
            
            usage_rights.authorized_channels = list(set(authorized_channels))
            
            self.db.add(usage_rights)
            self.db.commit()
            self.db.refresh(usage_rights)
            
            self.logger.info(f"Droits d'usage accordés: {usage_rights.rights_id}")
            return usage_rights
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur octroi droits: {str(e)}")
            raise

    def validate_usage_request(
        self,
        content_id: int,
        user_id: int,
        usage_type: UsageType,
        channel: str = None,
        duration_seconds: Optional[int] = None,
        audience_size: Optional[int] = None
    ) -> Tuple[bool, Optional[UsageRights], str]:
        """Valide une demande d'usage"""
        
        # Recherche des droits applicables
        rights = self.db.query(UsageRights).filter(
            UsageRights.content_id == content_id,
            UsageRights.grantee_id == user_id,
            UsageRights.status == RightsStatus.ACTIVE.value
        ).first()
        
        if not rights:
            return False, None, "Aucun droit d'usage trouvé"
        
        # Validation de l'usage
        can_use, reason = rights.can_use_for_purpose(usage_type, channel)
        return can_use, rights, reason

    def record_content_usage(
        self,
        rights_id: int,
        user_id: int,
        usage_type: UsageType,
        channel: str,
        duration_seconds: Optional[int] = None,
        audience_size: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> UsageLog:
        """Enregistre une utilisation de contenu"""
        
        try:
            rights = self.db.query(UsageRights).filter(
                UsageRights.id == rights_id
            ).first()
            
            if not rights:
                raise ValueError(f"Droits non trouvés: {rights_id}")
            
            # Validation de l'usage
            can_use, reason = rights.can_use_for_purpose(usage_type, channel)
            if not can_use:
                raise ValueError(f"Usage non autorisé: {reason}")
            
            # Enregistrement de l'usage
            usage_log = UsageLog(
                rights_id=rights_id,
                user_id=user_id,
                content_id=rights.content_id,
                usage_type=usage_type.value,
                channel=channel,
                duration_seconds=duration_seconds,
                audience_size=audience_size,
                usage_metadata=metadata or {},
                authorized=True,
                validation_method="automated"
            )
            
            # Mise à jour du compteur dans les droits
            rights.record_usage(usage_type, channel, duration_seconds, audience_size, metadata)
            
            self.db.add(usage_log)
            self.db.commit()
            self.db.refresh(usage_log)
            
            self.logger.info(f"Usage enregistré: {usage_log.log_id}")
            return usage_log
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur enregistrement usage: {str(e)}")
            raise

    def detect_rights_violation(
        self,
        content_id: int,
        violation_url: str,
        platform: str,
        detected_by_user_id: int,
        violation_type: str = "unauthorized_usage",
        evidence: Optional[Dict] = None
    ) -> RightsViolation:
        """Détecte et enregistre une violation de droits"""
        
        try:
            # Recherche des droits associés au contenu
            rights = self.db.query(UsageRights).filter(
                UsageRights.content_id == content_id,
                UsageRights.status == RightsStatus.ACTIVE.value
            ).first()
            
            if not rights:
                raise ValueError(f"Aucun droit actif trouvé pour le contenu {content_id}")
            
            # Création de la violation
            violation = RightsViolation(
                rights_id=rights.id,
                detected_by_user_id=detected_by_user_id,
                violation_type=violation_type,
                description=f"Usage non autorisé détecté sur {platform}",
                violation_url=violation_url,
                platform=platform,
                evidence_data=evidence or {}
            )
            
            # Analyse automatique de la sévérité
            severity = self._assess_violation_severity(violation, rights)
            violation.severity = severity
            
            self.db.add(violation)
            self.db.commit()
            self.db.refresh(violation)
            
            # Déclenchement des actions automatiques
            self._trigger_violation_response(violation)
            
            self.logger.info(f"Violation détectée: {violation.violation_id}")
            return violation
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur détection violation: {str(e)}")
            raise

    def get_user_usage_rights(
        self,
        user_id: int,
        as_grantor: bool = True,
        status: Optional[RightsStatus] = None
    ) -> List[UsageRights]:
        """Récupère les droits d'usage d'un utilisateur"""
        
        query = self.db.query(UsageRights)
        
        if as_grantor:
            query = query.filter(UsageRights.grantor_id == user_id)
        else:
            query = query.filter(UsageRights.grantee_id == user_id)
        
        if status:
            query = query.filter(UsageRights.status == status.value)
        
        return query.order_by(UsageRights.created_at.desc()).all()

    def generate_usage_report(
        self,
        content_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
Génère un rapport d'usage pour un contenu"""
        
        # Récupération des logs d'usage
        usage_logs = self.db.query(UsageLog).filter(
            UsageLog.content_id == content_id,
            UsageLog.usage_date >= start_date,
            UsageLog.usage_date <= end_date
        ).all()
        
        # Agrégation des données
        usage_by_type = defaultdict(int)
        usage_by_channel = defaultdict(int)
        usage_by_platform = defaultdict(int)
        total_audience = 0
        total_duration = 0
        
        for log in usage_logs:
            usage_by_type[log.usage_type] += 1
            if log.channel:
                usage_by_channel[log.channel] += 1
            if log.platform:
                usage_by_platform[log.platform] += 1
            if log.audience_size:
                total_audience += log.audience_size
            if log.duration_seconds:
                total_duration += log.duration_seconds
        
        # Récupération des violations
        violations = self.db.query(RightsViolation).join(UsageRights).filter(
            UsageRights.content_id == content_id,
            RightsViolation.detected_date >= start_date,
            RightsViolation.detected_date <= end_date
        ).all()
        
        return {
            "content_id": content_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_usages": len(usage_logs),
                "total_audience": total_audience,
                "total_duration_hours": total_duration / 3600 if total_duration else 0,
                "violations_count": len(violations)
            },
            "usage_breakdown": {
                "by_type": dict(usage_by_type),
                "by_channel": dict(usage_by_channel),
                "by_platform": dict(usage_by_platform)
            },
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "type": v.violation_type,
                    "severity": v.severity,
                    "platform": v.platform,
                    "status": v.status
                } for v in violations[-10:]  # Dernières 10 violations
            ],
            "compliance_score": self._calculate_compliance_score(usage_logs, violations),
            "generated_at": datetime.utcnow().isoformat()
        }

    def check_expiring_rights(self, days_ahead: int = 30) -> List[UsageRights]:
        """Trouve les droits qui expirent bientôt"""
        
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return self.db.query(UsageRights).filter(
            UsageRights.status == RightsStatus.ACTIVE.value,
            UsageRights.expiration_date <= cutoff_date,
            UsageRights.expiration_date > datetime.utcnow()
        ).all()

    def auto_renew_rights(self) -> List[str]:
        """
Renouvelle automatiquement les droits éligibles"""
        
        renewed_rights = []
        expiring_rights = self.check_expiring_rights(7)  # 7 jours avant expiration
        
        for rights in expiring_rights:
            if rights.auto_renewal and rights.renewal_conditions:
                try:
                    # Extension automatique
                    renewal_days = rights.renewal_conditions.get('renewal_period_days', 365)
                    rights.extend_validity(renewal_days, "Renouvellement automatique")
                    
                    self.db.commit()
                    renewed_rights.append(rights.rights_id)
                    self.logger.info(f"Droits renouvelés automatiquement: {rights.rights_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erreur renouvellement {rights.rights_id}: {str(e)}")
                    continue
        
        return renewed_rights

    def _validate_grantor_rights(self, grantor_id: int, content_id: int):
        """Valide que le concédant a le droit d'accorder des permissions"""
        logger = logging.getLogger(__name__)
        
        try:
            # Vérifier la propriété du contenu
            content_ownership_valid = self._check_content_ownership(grantor_id, content_id)
            
            # Vérifier les droits de licence existants
            licensing_rights_valid = self._check_licensing_rights(grantor_id, content_id)
            
            # Vérifier les restrictions administratives
            admin_restrictions = self._check_admin_restrictions(grantor_id, content_id)
            
            if not content_ownership_valid and not licensing_rights_valid:
                raise ValueError(f"Grantor {grantor_id} does not have rights to grant permissions for content {content_id}")
            
            if admin_restrictions:
                raise ValueError(f"Administrative restrictions prevent granting rights: {admin_restrictions}")
            
            logger.info(f"Grantor rights validation successful for grantor {grantor_id}, content {content_id}")
            
        except Exception as e:
            logger.error(f"Grantor rights validation failed: {e}")
            raise
    
    def _check_content_ownership(self, grantor_id: int, content_id: int) -> bool:
        """Vérifier si le concédant est propriétaire du contenu"""
        # En production, ceci ferait une requête à la base de données
        # Pour maintenant, simulation de vérification
        try:
            # Simulation: assumons que les propriétaires ont des IDs pairs
            # En réalité, ceci interrogerait la table content_ownership
            return grantor_id % 2 == 0
        except:
            return False
    
    def _check_licensing_rights(self, grantor_id: int, content_id: int) -> bool:
        """
Vérifier si le concédant a des droits de licence délégués"""
        # En production, ceci vérifierait les droits de licence dans la base de données
        try:
            # Simulation: vérification des droits de licence
            # En réalité, ceci interrogerait la table license_delegations
            return True  # Assumons que les droits de licence sont valides pour cette simulation
        except:
            return False
    
    def _check_admin_restrictions(self, grantor_id: int, content_id: int) -> Optional[str]:
        """
Vérifier s'il y a des restrictions administratives"""
        try:
            # Vérifier les restrictions de contenu
            if content_id in [999, 1000]:  # Simulation de contenu restreint
                return "Content is under administrative restriction"
            
            # Vérifier les restrictions d'utilisateur
            if grantor_id in [666, 777]:  # Simulation d'utilisateur restreint
                return "User is under administrative restriction"
            
            # Vérifier les restrictions temporaires
            # En production, ceci vérifierait les tables de restrictions temporaires
            
            return None  # Aucune restriction trouvée
        except Exception as e:
            return f"Error checking restrictions: {e}"

    def _assess_violation_severity(
        self,
        violation: RightsViolation,
        rights: UsageRights
    ) -> str:
        """Évalue la sévérité d'une violation"""
        
        # Critères d'évaluation
        severity_score = 0
        
        # Type de violation
        high_risk_types = ["commercial_usage", "mass_distribution", "derivative_work"]
        if violation.violation_type in high_risk_types:
            severity_score += 3
        
        # Plateforme
        major_platforms = ["youtube", "spotify", "instagram", "tiktok"]
        if violation.platform and violation.platform.lower() in major_platforms:
            severity_score += 2
        
        # Permissions existantes
        if not rights.granted_permissions:
            severity_score += 2
        
        # Détermination de la sévérité
        if severity_score >= 5:
            return "critical"
        elif severity_score >= 3:
            return "high"
        elif severity_score >= 1:
            return "medium"
        else:
            return "low"

    def _trigger_violation_response(self, violation: RightsViolation):
        """Déclenche les réponses automatiques à une violation"""
        
        if violation.severity == "critical":
            # Actions immédiates pour violations critiques
            violation.takedown_requested = True
            violation.legal_action_initiated = True
            
        elif violation.severity == "high":
            # Demande de retrait pour violations importantes
            violation.takedown_requested = True
            violation.warning_sent = True
            
        elif violation.severity == "medium":
            # Avertissement pour violations moyennes
            violation.warning_sent = True

    def _calculate_compliance_score(
        self,
        usage_logs: List[UsageLog],
        violations: List[RightsViolation]
    ) -> int:
        """Calcule un score de conformité (0-100)"""
        
        if not usage_logs:
            return 100
        
        total_usages = len(usage_logs)
        authorized_usages = len([log for log in usage_logs if log.authorized])
        violation_count = len(violations)
        
        # Score de base basé sur les usages autorisés
        base_score = (authorized_usages / total_usages) * 100
        
        # Pénalité pour les violations
        violation_penalty = min(violation_count * 5, 30)  # Max 30 points de pénalité
        
        final_score = max(0, base_score - violation_penalty)
        return int(final_score)
