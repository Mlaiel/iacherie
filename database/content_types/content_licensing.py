"""Content Licensing Module - Professional Rights Management System

Module avancé pour la gestion des licences, droits d'auteur et monétisation
automatisée du contenu dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Legal Technology Expert, Rights Management Specialist, Revenue Optimization Expert
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging
import uuid
import json
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .content_models import Base, ContentType

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Types of content licenses"""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    CREATIVE_COMMONS = "creative_commons"
    PUBLIC_DOMAIN = "public_domain"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    PERSONAL_USE = "personal_use"
    EDUCATIONAL = "educational"

class UsageScope(Enum):
    """Scope of content usage rights"""    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    ONLINE_ONLY = "online_only"
    PRINT_ONLY = "print_only"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"

class RevenueModel(Enum):
    """Revenue sharing models"""    FIXED_FEE = "fixed_fee"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    PER_USE = "per_use"
    SUBSCRIPTION = "subscription"
    REVENUE_SHARE = "revenue_share"
    HYBRID = "hybrid"
    NEGOTIABLE = "negotiable"

class LicenseStatus(Enum):
    """License agreement status"""    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    """Payment status for licenses"""    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    OVERDUE = "overdue"

class ComplianceStatus(Enum):
    """Compliance status for usage"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    VIOLATION = "violation"
    GRACE_PERIOD = "grace_period"

@dataclass
class LicenseTerms:
    """Container for license terms and conditions"""    usage_scope: UsageScope
    duration: timedelta
    territory: str
    exclusivity: bool
    commercial_use: bool
    modification_allowed: bool
    attribution_required: bool
    resale_allowed: bool
    
    # Financial terms
    base_fee: Decimal = Decimal('0.00')
    revenue_percentage: float = 0.0
    minimum_guarantee: Decimal = Decimal('0.00')
    maximum_liability: Decimal = Decimal('0.00')
    
    # Usage restrictions
    max_impressions: Optional[int] = None
    max_copies: Optional[int] = None
    restricted_platforms: List[str] = field(default_factory=list)
    approved_platforms: List[str] = field(default_factory=list)
    
    # Additional terms
    custom_clauses: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            'usage_scope': self.usage_scope.value,
            'duration_days': self.duration.days,
            'territory': self.territory,
            'exclusivity': self.exclusivity,
            'commercial_use': self.commercial_use,
            'modification_allowed': self.modification_allowed,
            'attribution_required': self.attribution_required,
            'resale_allowed': self.resale_allowed,
            'base_fee': str(self.base_fee),
            'revenue_percentage': self.revenue_percentage,
            'minimum_guarantee': str(self.minimum_guarantee),
            'maximum_liability': str(self.maximum_liability),
            'max_impressions': self.max_impressions,
            'max_copies': self.max_copies,
            'restricted_platforms': self.restricted_platforms,
            'approved_platforms': self.approved_platforms,
            'custom_clauses': self.custom_clauses
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LicenseTerms':
        """Create from dictionary"""        return cls(
            usage_scope=UsageScope(data['usage_scope']),
            duration=timedelta(days=data['duration_days']),
            territory=data['territory'],
            exclusivity=data['exclusivity'],
            commercial_use=data['commercial_use'],
            modification_allowed=data['modification_allowed'],
            attribution_required=data['attribution_required'],
            resale_allowed=data['resale_allowed'],
            base_fee=Decimal(data['base_fee']),
            revenue_percentage=data['revenue_percentage'],
            minimum_guarantee=Decimal(data['minimum_guarantee']),
            maximum_liability=Decimal(data['maximum_liability']),
            max_impressions=data.get('max_impressions'),
            max_copies=data.get('max_copies'),
            restricted_platforms=data.get('restricted_platforms', []),
            approved_platforms=data.get('approved_platforms', []),
            custom_clauses=data.get('custom_clauses', {})
        )

class ContentLicense(Base):
    """Database model for content licenses"""    __tablename__ = "content_licenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Content owner
    licensee_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # License buyer
    
    # License details
    license_type = Column(String(30), nullable=False, index=True)
    license_name = Column(String(255), nullable=False)
    license_description = Column(Text, nullable=True)
    license_version = Column(String(20), nullable=False, default='1.0')
    
    # Terms and conditions
    license_terms = Column(JSONB, nullable=False)
    usage_restrictions = Column(JSONB, nullable=False, default={})
    allowed_platforms = Column(ARRAY(String), nullable=False, default=[])
    prohibited_platforms = Column(ARRAY(String), nullable=False, default=[])
    
    # Financial terms
    revenue_model = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    revenue_percentage = Column(Float, nullable=False, default=0.0)
    minimum_payment = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default='EUR')
    
    # Validity and status
    status = Column(String(20), nullable=False, default='draft', index=True)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    auto_renewal = Column(Boolean, nullable=False, default=False)
    renewal_period_days = Column(Integer, nullable=True)
    
    # Usage tracking
    total_usage_count = Column(Integer, nullable=False, default=0)
    total_impressions = Column(Integer, nullable=False, default=0)
    total_revenue_generated = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    last_usage_date = Column(DateTime(timezone=True), nullable=True)
    
    # Legal and compliance
    copyright_notice = Column(Text, nullable=True)
    attribution_text = Column(Text, nullable=True)
    dmca_agent_info = Column(JSONB, nullable=True)
    compliance_status = Column(String(20), nullable=False, default='compliant')
    
    # Contract information
    contract_document_url = Column(Text, nullable=True)
    digital_signature = Column(Text, nullable=True)
    signed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    license_metadata = Column(JSONB, nullable=False, default={})
    usage_analytics = Column(JSONB, nullable=False, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    terminated_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<ContentLicense(id={self.id}, type={self.license_type}, status={self.status})>"
    
    def get_terms(self) -> LicenseTerms:
        """Get license terms as typed object"""        return LicenseTerms.from_dict(self.license_terms)
    
    def set_terms(self, terms: LicenseTerms):
        """Set license terms from typed object"""        self.license_terms = terms.to_dict()
    
    def is_active(self) -> bool:
        """Check if license is currently active"""        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return (
            self.status == LicenseStatus.ACTIVE.value and
            self.valid_from <= now and
            (self.valid_until is None or self.valid_until >= now)
        )
    
    def is_expired(self) -> bool:
        """Check if license has expired"""        if self.valid_until is None:
            return False
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return self.valid_until < now
    
    def calculate_revenue(self, usage_count: int = 0, gross_revenue: Decimal = Decimal('0.00')) -> Decimal:
        """Calculate revenue based on license terms"""        if self.revenue_model == RevenueModel.FIXED_FEE.value:
            return self.base_price
        
        elif self.revenue_model == RevenueModel.PERCENTAGE.value:
            return gross_revenue * Decimal(str(self.revenue_percentage / 100))
        
        elif self.revenue_model == RevenueModel.PER_USE.value:
            return self.base_price * Decimal(str(usage_count))
        
        elif self.revenue_model == RevenueModel.REVENUE_SHARE.value:
            revenue_share = gross_revenue * Decimal(str(self.revenue_percentage / 100))
            return max(revenue_share, self.minimum_payment)
        
        else:
            return Decimal('0.00')

class LicenseUsage(Base):
    """Database model for license usage tracking"""    __tablename__ = "license_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey('content_licenses.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Usage details
    platform = Column(String(50), nullable=False, index=True)
    usage_type = Column(String(30), nullable=False)  # view, download, stream, embed, etc.
    usage_url = Column(Text, nullable=True)
    usage_context = Column(String(100), nullable=True)  # social_post, website, advertisement, etc.
    
    # Metrics
    impression_count = Column(Integer, nullable=False, default=1)
    duration_seconds = Column(Integer, nullable=True)
    audience_size = Column(Integer, nullable=True)
    engagement_metrics = Column(JSONB, nullable=False, default={})
    
    # Revenue tracking
    gross_revenue = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    license_fee = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    net_revenue = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default='EUR')
    
    # Compliance
    compliance_status = Column(String(20), nullable=False, default='compliant')
    attribution_provided = Column(Boolean, nullable=False, default=False)
    usage_approved = Column(Boolean, nullable=False, default=True)
    
    # Geographic and demographic data
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    audience_demographics = Column(JSONB, nullable=False, default={})
    
    # Technical metadata
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    referrer_url = Column(Text, nullable=True)
    device_type = Column(String(20), nullable=True)
    
    # Timestamps
    usage_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    license = relationship("ContentLicense", back_populates="usage_records")
    
    def __repr__(self) -> str:
        return f"<LicenseUsage(id={self.id}, platform={self.platform}, type={self.usage_type})>"

class RevenueTransaction(Base):
    """Database model for revenue transactions"""    __tablename__ = "revenue_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey('content_licenses.id'), nullable=False)
    usage_id = Column(UUID(as_uuid=True), ForeignKey('license_usage.id'), nullable=True)
    
    # Transaction details
    transaction_type = Column(String(30), nullable=False)  # license_fee, revenue_share, penalty, refund
    transaction_reference = Column(String(100), nullable=True, unique=True)
    
    # Financial details
    gross_amount = Column(DECIMAL(12, 2), nullable=False)
    fee_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    tax_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    net_amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='EUR')
    
    # Payment information
    payment_method = Column(String(50), nullable=True)
    payment_processor = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_status = Column(String(20), nullable=False, default='pending')
    
    # Recipient information
    payer_id = Column(UUID(as_uuid=True), nullable=False)
    payee_id = Column(UUID(as_uuid=True), nullable=False)
    payout_schedule = Column(String(20), nullable=False, default='immediate')  # immediate, weekly, monthly
    
    # Processing details
    processed_at = Column(DateTime(timezone=True), nullable=True)
    settlement_date = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    transaction_metadata = Column(JSONB, nullable=False, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    license = relationship("ContentLicense")
    usage = relationship("LicenseUsage")
    
    def __repr__(self) -> str:
        return f"<RevenueTransaction(id={self.id}, amount={self.net_amount}, status={self.payment_status})>"

class LicenseManager:
    """High-level license management system"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.default_currency = self.config.get('default_currency', 'EUR')
        self.platform_fees = self.config.get('platform_fees', {})
    
    def create_standard_license(self, content_id: str, owner_id: str,
                              license_type: LicenseType,
                              terms: LicenseTerms) -> ContentLicense:
        """Create a standard content license"""        try:
            license = ContentLicense(
                content_id=content_id,
                owner_id=owner_id,
                license_type=license_type.value,
                license_name=f"{license_type.value.title()} License",
                license_description=f"Standard {license_type.value} license for content usage",
                license_terms=terms.to_dict(),
                revenue_model=RevenueModel.PERCENTAGE.value if terms.revenue_percentage > 0 else RevenueModel.FIXED_FEE.value,
                base_price=terms.base_fee,
                revenue_percentage=terms.revenue_percentage,
                minimum_payment=terms.minimum_guarantee,
                valid_from=datetime.utcnow().replace(tzinfo=timezone.utc),
                valid_until=datetime.utcnow().replace(tzinfo=timezone.utc) + terms.duration if terms.duration.total_seconds() > 0 else None,
                allowed_platforms=terms.approved_platforms,
                prohibited_platforms=terms.restricted_platforms
            )
            
            return license
            
        except Exception as e:
            self.logger.error(f"License creation failed: {e}")
            raise
    
    def create_creative_commons_license(self, content_id: str, owner_id: str,
                                      cc_variant: str = "CC-BY") -> ContentLicense:
        """Create Creative Commons license"""        cc_terms = {
            "CC-BY": LicenseTerms(
                usage_scope=UsageScope.GLOBAL,
                duration=timedelta(days=365*100),  # Effectively perpetual
                territory="Worldwide",
                exclusivity=False,
                commercial_use=True,
                modification_allowed=True,
                attribution_required=True,
                resale_allowed=True
            ),
            "CC-BY-NC": LicenseTerms(
                usage_scope=UsageScope.GLOBAL,
                duration=timedelta(days=365*100),
                territory="Worldwide",
                exclusivity=False,
                commercial_use=False,
                modification_allowed=True,
                attribution_required=True,
                resale_allowed=False
            ),
            "CC-BY-SA": LicenseTerms(
                usage_scope=UsageScope.GLOBAL,
                duration=timedelta(days=365*100),
                territory="Worldwide",
                exclusivity=False,
                commercial_use=True,
                modification_allowed=True,
                attribution_required=True,
                resale_allowed=True,
                custom_clauses={"share_alike": True}
            )
        }
        
        terms = cc_terms.get(cc_variant, cc_terms["CC-BY"])
        
        license = self.create_standard_license(
            content_id, owner_id, LicenseType.CREATIVE_COMMONS, terms
        )
        
        license.license_name = f"Creative Commons {cc_variant}"
        license.license_description = f"Creative Commons {cc_variant} license allowing {cc_variant} usage"
        license.copyright_notice = f"Licensed under {cc_variant}"
        license.attribution_text = "Content by [Creator Name] licensed under {cc_variant}"
        
        return license
    
    def create_royalty_free_license(self, content_id: str, owner_id: str,
                                  price: Decimal = Decimal('0.00')) -> ContentLicense:
        """Create royalty-free license"""        terms = LicenseTerms(
            usage_scope=UsageScope.GLOBAL,
            duration=timedelta(days=365*100),  # Effectively perpetual
            territory="Worldwide",
            exclusivity=False,
            commercial_use=True,
            modification_allowed=True,
            attribution_required=False,
            resale_allowed=False,
            base_fee=price
        )
        
        license = self.create_standard_license(
            content_id, owner_id, LicenseType.ROYALTY_FREE, terms
        )
        
        license.revenue_model = RevenueModel.FIXED_FEE.value
        license.license_name = "Royalty-Free License"
        license.license_description = "One-time payment for unlimited usage rights"
        
        return license
    
    def track_usage(self, license_id: str, platform: str, usage_type: str,
                   usage_data: Dict[str, Any]) -> LicenseUsage:
        """Track license usage"""        try:
            usage = LicenseUsage(
                license_id=license_id,
                user_id=usage_data.get('user_id'),
                platform=platform,
                usage_type=usage_type,
                usage_url=usage_data.get('url'),
                usage_context=usage_data.get('context'),
                impression_count=usage_data.get('impressions', 1),
                duration_seconds=usage_data.get('duration'),
                audience_size=usage_data.get('audience_size'),
                engagement_metrics=usage_data.get('engagement', {}),
                gross_revenue=Decimal(str(usage_data.get('revenue', 0.00))),
                country_code=usage_data.get('country'),
                region=usage_data.get('region'),
                audience_demographics=usage_data.get('demographics', {}),
                user_agent=usage_data.get('user_agent'),
                ip_address=usage_data.get('ip_address'),
                referrer_url=usage_data.get('referrer'),
                device_type=usage_data.get('device_type')
            )
            
            return usage
            
        except Exception as e:
            self.logger.error(f"Usage tracking failed: {e}")
            raise
    
    def calculate_license_revenue(self, license: ContentLicense, 
                                usage: LicenseUsage) -> RevenueTransaction:
        """Calculate and create revenue transaction"""        try:
            # Calculate license fee based on revenue model
            license_fee = license.calculate_revenue(
                usage_count=usage.impression_count,
                gross_revenue=usage.gross_revenue
            )
            
            # Calculate platform fees
            platform_fee_rate = self.platform_fees.get(usage.platform, 0.05)  # 5% default
            platform_fee = license_fee * Decimal(str(platform_fee_rate))
            
            # Calculate tax (placeholder - would integrate with tax service)
            tax_rate = Decimal('0.20')  # 20% VAT placeholder
            tax_amount = license_fee * tax_rate
            
            net_amount = license_fee - platform_fee - tax_amount
            
            transaction = RevenueTransaction(
                license_id=license.id,
                usage_id=usage.id,
                transaction_type='license_fee',
                gross_amount=license_fee,
                fee_amount=platform_fee,
                tax_amount=tax_amount,
                net_amount=net_amount,
                currency=license.currency,
                payer_id=usage.user_id,
                payee_id=license.owner_id,
                transaction_metadata={
                    'usage_type': usage.usage_type,
                    'platform': usage.platform,
                    'impressions': usage.impression_count,
                    'calculation_method': license.revenue_model
                }
            )
            
            return transaction
            
        except Exception as e:
            self.logger.error(f"Revenue calculation failed: {e}")
            raise
    
    def check_compliance(self, license: ContentLicense, usage: LicenseUsage) -> bool:
        """Check if usage complies with license terms"""        try:
            terms = license.get_terms()
            
            # Check platform restrictions
            if terms.restricted_platforms and usage.platform in terms.restricted_platforms:
                return False
            
            if terms.approved_platforms and usage.platform not in terms.approved_platforms:
                return False
            
            # Check commercial use restrictions
            if not terms.commercial_use and usage.gross_revenue > 0:
                return False
            
            # Check attribution requirements
            if terms.attribution_required and not usage.attribution_provided:
                return False
            
            # Check usage limits
            if terms.max_impressions and usage.impression_count > terms.max_impressions:
                return False
            
            # Check license validity
            if not license.is_active():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return False
    
    def generate_license_report(self, license_id: str, 
                              start_date: datetime = None,
                              end_date: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive license usage report"""        try:
            # This would query the database for usage data
            # For now, return a template structure
            
            report = {
                'license_id': license_id,
                'report_period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'usage_summary': {
                    'total_usage_count': 0,
                    'total_impressions': 0,
                    'unique_users': 0,
                    'platforms_used': []
                },
                'revenue_summary': {
                    'total_gross_revenue': '0.00',
                    'total_license_fees': '0.00',
                    'total_net_revenue': '0.00',
                    'currency': self.default_currency
                },
                'compliance_summary': {
                    'compliant_usage': 0,
                    'non_compliant_usage': 0,
                    'attribution_rate': 0.0,
                    'violations': []
                },
                'geographic_breakdown': {},
                'platform_breakdown': {},
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

# Add relationships to existing models
ContentLicense.usage_records = relationship("LicenseUsage", back_populates="license")

# Export all classes and enums
__all__ = [
    'LicenseType',
    'UsageScope',
    'RevenueModel',
    'LicenseStatus',
    'PaymentStatus',
    'ComplianceStatus',
    'LicenseTerms',
    'ContentLicense',
    'LicenseUsage',
    'RevenueTransaction',
    'LicenseManager'
]
