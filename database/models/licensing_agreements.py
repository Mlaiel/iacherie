"""Licensing Agreements Database Model

Enterprise-grade SQLAlchemy model for managing content licensing, usage rights,
and legal agreements for content protection and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone, date
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class LicenseType(Enum):
    """
License type enumeration"""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"
    PUBLISHING_LICENSE = "publishing_license"
    SAMPLING_LICENSE = "sampling_license"
    REMIX_LICENSE = "remix_license"
    COVER_LICENSE = "cover_license"
    DISTRIBUTION_LICENSE = "distribution_license"
    BROADCAST_LICENSE = "broadcast_license"
    STREAMING_LICENSE = "streaming_license"
    DOWNLOAD_LICENSE = "download_license"
    COMMERCIAL_LICENSE = "commercial_license"
    EDUCATIONAL_LICENSE = "educational_license"
    PERSONAL_LICENSE = "personal_license"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    CUSTOM = "custom"


class LicenseStatus(Enum):
    """License status enumeration"""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    RENEGOTIATING = "renegotiating"
    RENEWED = "renewed"


class UsageRight(Enum):
    """Usage rights enumeration"""

    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    SYNCHRONIZATION = "synchronization"
    ADAPTATION = "adaptation"
    TRANSLATION = "translation"
    REMIX = "remix"
    SAMPLING = "sampling"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    MECHANICAL = "mechanical"
    DIGITAL_DELIVERY = "digital_delivery"
    PHYSICAL_DISTRIBUTION = "physical_distribution"
    COMMERCIAL_USE = "commercial_use"
    ADVERTISING = "advertising"
    FILM_TV = "film_tv"
    GAMING = "gaming"
    CORPORATE_USE = "corporate_use"
    EDUCATIONAL_USE = "educational_use"
    NON_PROFIT_USE = "non_profit_use"


class RevenueModel(Enum):
    """Revenue model enumeration"""

    FLAT_FEE = "flat_fee"
    PERCENTAGE_ROYALTY = "percentage_royalty"
    PER_UNIT = "per_unit"
    PER_STREAM = "per_stream"
    PER_DOWNLOAD = "per_download"
    PER_VIEW = "per_view"
    SUBSCRIPTION_SHARE = "subscription_share"
    ADVERTISING_SHARE = "advertising_share"
    HYBRID = "hybrid"
    REVENUE_SHARE = "revenue_share"
    MINIMUM_GUARANTEE = "minimum_guarantee"
    ADVANCE_RECOUPABLE = "advance_recoupable"
    BUYOUT = "buyout"
    CUSTOM = "custom"


class TerritoryScope(Enum):
    """Territory scope enumeration"""

    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    SPECIFIC_COUNTRIES = "specific_countries"
    EXCLUDING_COUNTRIES = "excluding_countries"
    DIGITAL_ONLY = "digital_only"
    PHYSICAL_ONLY = "physical_only"


class LicensingAgreement(Base):
    """
    Enterprise Licensing Agreement Model
    
    Comprehensive licensing system for content usage rights, revenue sharing,
    and legal compliance with automated enforcement and tracking.
    """
    __tablename__ = "licensing_agreements"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    licensor_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)  # Content owner
    licensee_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)  # License buyer
    
    # Agreement identification
    agreement_number = Column(String(100), unique=True, nullable=False, index=True)
    agreement_title = Column(String(500), nullable=False)
    agreement_description = Column(Text, nullable=True)
    external_reference = Column(String(255), nullable=True)  # External contract reference
    
    # License classification
    license_type = Column(SQLEnum(LicenseType), nullable=False, index=True)
    license_status = Column(SQLEnum(LicenseStatus), default=LicenseStatus.DRAFT, index=True)
    license_category = Column(String(100), nullable=True)
    license_subcategory = Column(String(100), nullable=True)
    
    # Parties information
    licensor_name = Column(String(255), nullable=False)
    licensor_email = Column(String(255), nullable=True)
    licensor_organization = Column(String(255), nullable=True)
    licensor_address = Column(JSON, nullable=True)
    licensor_contact_details = Column(JSON, nullable=True)
    
    licensee_name = Column(String(255), nullable=True)
    licensee_email = Column(String(255), nullable=True)
    licensee_organization = Column(String(255), nullable=True)
    licensee_address = Column(JSON, nullable=True)
    licensee_contact_details = Column(JSON, nullable=True)
    
    # Content details
    content_title = Column(String(500), nullable=True)
    content_artist = Column(String(255), nullable=True)
    content_album = Column(String(255), nullable=True)
    content_duration = Column(Float, nullable=True)
    content_isrc = Column(String(20), nullable=True)
    content_metadata = Column(JSON, nullable=True)
    
    # Usage rights and permissions
    usage_rights = Column(ARRAY(SQLEnum(UsageRight)), nullable=False)
    usage_restrictions = Column(JSON, nullable=True)
    usage_limitations = Column(JSON, nullable=True)
    prohibited_uses = Column(JSON, nullable=True)
    attribution_requirements = Column(JSON, nullable=True)
    
    # Geographic and temporal scope
    territory_scope = Column(SQLEnum(TerritoryScope), default=TerritoryScope.WORLDWIDE)
    included_territories = Column(ARRAY(String), nullable=True)
    excluded_territories = Column(ARRAY(String), nullable=True)
    territory_restrictions = Column(JSON, nullable=True)
    
    # Time periods
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    term_duration = Column(Integer, nullable=True)  # Duration in days
    term_type = Column(String(50), nullable=True)  # perpetual, fixed, renewable
    auto_renewal = Column(Boolean, default=False)
    renewal_terms = Column(JSON, nullable=True)
    
    # Financial terms
    revenue_model = Column(SQLEnum(RevenueModel), nullable=False)
    license_fee = Column(Numeric(15, 4), nullable=True)
    royalty_percentage = Column(Float, nullable=True)
    minimum_guarantee = Column(Numeric(15, 4), nullable=True)
    advance_amount = Column(Numeric(15, 4), nullable=True)
    per_unit_rate = Column(Numeric(10, 4), nullable=True)
    currency = Column(String(3), default="EUR")
    
    # Revenue sharing details
    revenue_splits = Column(JSON, nullable=True)
    payment_terms = Column(JSON, nullable=True)
    payment_frequency = Column(String(50), nullable=True)  # monthly, quarterly, annual
    payment_threshold = Column(Numeric(10, 2), nullable=True)
    accounting_period = Column(String(50), nullable=True)
    
    # Performance metrics and limits
    usage_limits = Column(JSON, nullable=True)
    performance_thresholds = Column(JSON, nullable=True)
    quality_requirements = Column(JSON, nullable=True)
    delivery_requirements = Column(JSON, nullable=True)
    reporting_requirements = Column(JSON, nullable=True)
    
    # Compliance and legal
    governing_law = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)
    dispute_resolution = Column(String(100), nullable=True)
    termination_clauses = Column(JSON, nullable=True)
    breach_remedies = Column(JSON, nullable=True)
    force_majeure = Column(JSON, nullable=True)
    
    # Digital rights management
    drm_requirements = Column(JSON, nullable=True)
    watermarking_required = Column(Boolean, default=False)
    copy_protection = Column(JSON, nullable=True)
    access_controls = Column(JSON, nullable=True)
    usage_tracking = Column(JSON, nullable=True)
    
    # Approval and execution
    requires_approval = Column(Boolean, default=True)
    approval_workflow = Column(JSON, nullable=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    witness_details = Column(JSON, nullable=True)
    
    # Document management
    contract_documents = Column(JSON, nullable=True)
    amendment_history = Column(JSON, nullable=True)
    version_number = Column(String(20), default="1.0")
    parent_agreement_id = Column(UUID(as_uuid=True), ForeignKey('licensing_agreements.id'), nullable=True)
    superseded_agreement_id = Column(UUID(as_uuid=True), ForeignKey('licensing_agreements.id'), nullable=True)
    
    # Performance tracking
    usage_statistics = Column(JSON, nullable=True)
    revenue_generated = Column(Numeric(15, 4), default=0.0)
    revenue_outstanding = Column(Numeric(15, 4), default=0.0)
    payments_made = Column(Numeric(15, 4), default=0.0)
    last_payment_date = Column(DateTime(timezone=True), nullable=True)
    next_payment_due = Column(DateTime(timezone=True), nullable=True)
    
    # Compliance monitoring
    compliance_status = Column(String(50), default="compliant")
    compliance_checks = Column(JSON, nullable=True)
    violation_count = Column(Integer, default=0)
    violation_history = Column(JSON, nullable=True)
    remediation_actions = Column(JSON, nullable=True)
    
    # Automation and AI
    auto_enforcement_enabled = Column(Boolean, default=True)
    ai_monitoring_enabled = Column(Boolean, default=True)
    automated_reporting = Column(Boolean, default=True)
    smart_contract_address = Column(String(255), nullable=True)
    blockchain_hash = Column(String(255), nullable=True)
    
    # Communication and notifications
    notification_settings = Column(JSON, nullable=True)
    communication_log = Column(JSON, nullable=True)
    escalation_procedures = Column(JSON, nullable=True)
    contact_preferences = Column(JSON, nullable=True)
    
    # Platform integration
    platform_specific_terms = Column(JSON, nullable=True)
    distribution_channels = Column(JSON, nullable=True)
    platform_restrictions = Column(JSON, nullable=True)
    sync_requirements = Column(JSON, nullable=True)
    
    # Risk assessment
    risk_level = Column(String(50), default="low")
    risk_factors = Column(JSON, nullable=True)
    insurance_requirements = Column(JSON, nullable=True)
    liability_limits = Column(JSON, nullable=True)
    indemnification_terms = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    signed_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_due = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    is_master_agreement = Column(Boolean, default=False)
    is_exclusive = Column(Boolean, default=False)
    is_perpetual = Column(Boolean, default=False)
    requires_signature = Column(Boolean, default=True)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="licensing_agreements")
    revenue_records = relationship("RevenueTracking", back_populates="licensing_agreement", cascade="all, delete-orphan")
    parent_agreement = relationship("LicensingAgreement", remote_side=[id], foreign_keys=[parent_agreement_id])
    superseded_agreement = relationship("LicensingAgreement", remote_side=[id], foreign_keys=[superseded_agreement_id])
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_licensing_licensor_status', 'licensor_user_id', 'license_status'),
        Index('idx_licensing_licensee_type', 'licensee_user_id', 'license_type'),
        Index('idx_licensing_content_fingerprint', 'content_fingerprint_id', 'license_status'),
        Index('idx_licensing_effective_expiration', 'effective_date', 'expiration_date'),
        Index('idx_licensing_territory_scope', 'territory_scope', 'license_type'),
        Index('idx_licensing_revenue_model', 'revenue_model', 'currency'),
        Index('idx_licensing_approval_status', 'requires_approval', 'approved_at'),
        Index('idx_licensing_compliance', 'compliance_status', 'violation_count'),
        Index('idx_licensing_automation', 'auto_enforcement_enabled', 'ai_monitoring_enabled'),
        Index('idx_licensing_payment_due', 'next_payment_due', 'license_status'),
        Index('idx_licensing_agreement_number', 'agreement_number'),
    )
    
    def __repr__(self):
        try:
            logger.info(f"Executing __repr__")
            
            # Implementation for __repr__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__repr__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__repr__ failed: {e}")
            raise
    def to_dict(self, include_sensitive: bool = False, include_analytics: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        base_dict = {
            "id": str(self.id),
            "content_fingerprint_id": str(self.content_fingerprint_id) if self.content_fingerprint_id else None,
            "licensor_user_id": str(self.licensor_user_id),
            "licensee_user_id": str(self.licensee_user_id) if self.licensee_user_id else None,
            "agreement_number": self.agreement_number,
            "agreement_title": self.agreement_title,
            "agreement_description": self.agreement_description,
            "external_reference": self.external_reference,
            "license_type": self.license_type.value if self.license_type else None,
            "license_status": self.license_status.value if self.license_status else None,
            "license_category": self.license_category,
            "license_subcategory": self.license_subcategory,
            "licensor_name": self.licensor_name,
            "licensor_organization": self.licensor_organization,
            "licensee_name": self.licensee_name,
            "licensee_organization": self.licensee_organization,
            "content_title": self.content_title,
            "content_artist": self.content_artist,
            "content_album": self.content_album,
            "content_duration": self.content_duration,
            "content_isrc": self.content_isrc,
            "usage_rights": [ur.value for ur in self.usage_rights] if self.usage_rights else [],
            "usage_restrictions": self.usage_restrictions,
            "usage_limitations": self.usage_limitations,
            "prohibited_uses": self.prohibited_uses,
            "attribution_requirements": self.attribution_requirements,
            "territory_scope": self.territory_scope.value if self.territory_scope else None,
            "included_territories": self.included_territories,
            "excluded_territories": self.excluded_territories,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "term_duration": self.term_duration,
            "term_type": self.term_type,
            "auto_renewal": self.auto_renewal,
            "renewal_terms": self.renewal_terms,
            "revenue_model": self.revenue_model.value if self.revenue_model else None,
            "license_fee": float(self.license_fee) if self.license_fee else None,
            "royalty_percentage": self.royalty_percentage,
            "minimum_guarantee": float(self.minimum_guarantee) if self.minimum_guarantee else None,
            "advance_amount": float(self.advance_amount) if self.advance_amount else None,
            "per_unit_rate": float(self.per_unit_rate) if self.per_unit_rate else None,
            "currency": self.currency,
            "revenue_splits": self.revenue_splits,
            "payment_terms": self.payment_terms,
            "payment_frequency": self.payment_frequency,
            "payment_threshold": float(self.payment_threshold) if self.payment_threshold else None,
            "usage_limits": self.usage_limits,
            "performance_thresholds": self.performance_thresholds,
            "quality_requirements": self.quality_requirements,
            "governing_law": self.governing_law,
            "jurisdiction": self.jurisdiction,
            "dispute_resolution": self.dispute_resolution,
            "drm_requirements": self.drm_requirements,
            "watermarking_required": self.watermarking_required,
            "copy_protection": self.copy_protection,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "version_number": self.version_number,
            "parent_agreement_id": str(self.parent_agreement_id) if self.parent_agreement_id else None,
            "compliance_status": self.compliance_status,
            "violation_count": self.violation_count,
            "auto_enforcement_enabled": self.auto_enforcement_enabled,
            "ai_monitoring_enabled": self.ai_monitoring_enabled,
            "automated_reporting": self.automated_reporting,
            "smart_contract_address": self.smart_contract_address,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "next_review_due": self.next_review_due.isoformat() if self.next_review_due else None,
            "is_active": self.is_active,
            "is_template": self.is_template,
            "is_master_agreement": self.is_master_agreement,
            "is_exclusive": self.is_exclusive,
            "is_perpetual": self.is_perpetual,
            "requires_signature": self.requires_signature
        }
        
        if include_sensitive and include_analytics:
            base_dict.update({
                "licensor_email": self.licensor_email,
                "licensee_email": self.licensee_email,
                "licensor_address": self.licensor_address,
                "licensee_address": self.licensee_address,
                "revenue_generated": float(self.revenue_generated),
                "revenue_outstanding": float(self.revenue_outstanding),
                "payments_made": float(self.payments_made),
                "last_payment_date": self.last_payment_date.isoformat() if self.last_payment_date else None,
                "next_payment_due": self.next_payment_due.isoformat() if self.next_payment_due else None,
                "usage_statistics": self.usage_statistics,
                "compliance_checks": self.compliance_checks,
                "violation_history": self.violation_history
            })
        
        return base_dict
    
    def is_expired(self) -> bool:
        """Check if agreement is expired"""
        if not self.expiration_date:
            return False
        return datetime.now(timezone.utc) >= self.expiration_date
    
    def is_effective(self) -> bool:
        """
Check if agreement is currently effective"""
        now = datetime.now(timezone.utc)
        return (
            self.effective_date <= now and
            (not self.expiration_date or self.expiration_date > now) and
            self.license_status == LicenseStatus.ACTIVE
        )
    
    def days_until_expiration(self) -> Optional[int]:
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
Calculate days until expiration"""
        if not self.expiration_date:
            return None
        
        delta = self.expiration_date - datetime.now(timezone.utc)
        return max(delta.days, 0)
    
    def calculate_revenue_share(self, gross_revenue: Decimal) -> Dict[str, Decimal]:
        """
Calculate revenue shares based on agreement terms"""
        if self.revenue_model == RevenueModel.PERCENTAGE_ROYALTY and self.royalty_percentage:
            royalty_amount = gross_revenue * Decimal(str(self.royalty_percentage / 100))
            return {
                "gross_revenue": gross_revenue,
                "royalty_amount": royalty_amount,
                "net_revenue": gross_revenue - royalty_amount,
                "royalty_percentage": Decimal(str(self.royalty_percentage))
            }
        elif self.revenue_model == RevenueModel.FLAT_FEE:
            return {
                "gross_revenue": gross_revenue,
                "flat_fee": self.license_fee or Decimal('0'),
                "net_revenue": gross_revenue - (self.license_fee or Decimal('0'))
            }
        
        return {"gross_revenue": gross_revenue, "net_revenue": gross_revenue}
    
    def needs_review(self) -> bool:
        """Check if agreement needs review"""
        if not self.next_review_due:
            return False
        return datetime.now(timezone.utc) >= self.next_review_due
    
    def is_compliant(self) -> bool:
        """
Check overall compliance status"""
        return (
            self.compliance_status == "compliant" and
            self.violation_count < 3 and
            not self.is_expired() and
            self.is_effective()
        )
    
    @classmethod
    def create_agreement(cls, agreement_data: Dict[str, Any], licensor_user_id: str) -> 'LicensingAgreement':
        """Create LicensingAgreement from agreement data"""
        # Generate unique agreement number
        agreement_number = f"LIC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return cls(
            content_fingerprint_id=agreement_data.get('content_fingerprint_id'),
            licensor_user_id=licensor_user_id,
            licensee_user_id=agreement_data.get('licensee_user_id'),
            agreement_number=agreement_number,
            agreement_title=agreement_data.get('agreement_title'),
            agreement_description=agreement_data.get('agreement_description'),
            license_type=LicenseType(agreement_data.get('license_type', 'non_exclusive')),
            licensor_name=agreement_data.get('licensor_name'),
            licensor_email=agreement_data.get('licensor_email'),
            licensor_organization=agreement_data.get('licensor_organization'),
            licensee_name=agreement_data.get('licensee_name'),
            licensee_email=agreement_data.get('licensee_email'),
            licensee_organization=agreement_data.get('licensee_organization'),
            content_title=agreement_data.get('content_title'),
            content_artist=agreement_data.get('content_artist'),
            usage_rights=agreement_data.get('usage_rights', []),
            territory_scope=TerritoryScope(agreement_data.get('territory_scope', 'worldwide')),
            effective_date=agreement_data.get('effective_date', datetime.now(timezone.utc)),
            expiration_date=agreement_data.get('expiration_date'),
            revenue_model=RevenueModel(agreement_data.get('revenue_model', 'percentage_royalty')),
            license_fee=Decimal(str(agreement_data.get('license_fee', 0.0))),
            royalty_percentage=agreement_data.get('royalty_percentage'),
            currency=agreement_data.get('currency', 'EUR'),
            governing_law=agreement_data.get('governing_law'),
            jurisdiction=agreement_data.get('jurisdiction'),
            requires_approval=agreement_data.get('requires_approval', True)
        )
