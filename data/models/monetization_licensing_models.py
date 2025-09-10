"""Monetization Licensing Models
=============================

Enterprise monetization and licensing models for IA Influencer Agent platform.
Comprehensive revenue tracking, automated licensing, and multi-currency support
with performance-based pricing algorithms and legal compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 ENTERPRISE FEATURES:
• Multi-source revenue tracking & optimization
• Automated licensing agreement generation
• Real-time royalty calculation & distribution
• Multi-currency & cryptocurrency support
• Performance-based pricing algorithms
• Legal compliance & contract management
• Revenue forecasting & analytics
• Creator payment automation
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Index, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
import uuid
from typing import Optional, Dict, Any, List

# Import base from enterprise content models
from .enterprise_content_models import Base

# ============================================================================
# ENUMS - Revenue Management
# ============================================================================

class RevenueSource(Enum):
    """Revenue sources for content monetization"""
    ADS = "ads"
    SUBSCRIPTIONS = "subscriptions"
    LICENSING = "licensing"
    DONATIONS = "donations"
    NFT_SALES = "nft_sales"
    MERCHANDISE = "merchandise"
    SPONSORSHIPS = "sponsorships"
    AFFILIATE = "affiliate"
    DIRECT_SALES = "direct_sales"
    STREAMING_ROYALTIES = "streaming_royalties"
    PERFORMANCE_ROYALTIES = "performance_royalties"
    SYNC_LICENSING = "sync_licensing"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    COURSE_SALES = "course_sales"
    CONSULTATION = "consultation"


class RevenueStatus(Enum):
    """Status of revenue transactions"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PAID = "paid"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    FAILED = "failed"
    ON_HOLD = "on_hold"
    WITHHELD = "withheld"


class PaymentMethod(Enum):
    """Supported payment methods"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    WISE = "wise"
    CRYPTO_BITCOIN = "crypto_bitcoin"
    CRYPTO_ETHEREUM = "crypto_ethereum"
    CRYPTO_USDC = "crypto_usdc"
    CRYPTO_USDT = "crypto_usdt"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SEPA = "sepa"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    CHECK = "check"


class RevenuePeriod(Enum):
    """Revenue reporting and calculation periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


# ============================================================================
# ENUMS - Licensing Management
# ============================================================================

class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    CUSTOM = "custom"
    SYNC_LICENSE = "sync_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    MASTER_LICENSE = "master_license"


class LicenseCategory(Enum):
    """License usage categories"""
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EDUCATIONAL = "educational"
    EDITORIAL = "editorial"
    BROADCAST = "broadcast"
    THEATRICAL = "theatrical"
    DIGITAL = "digital"
    PRINT = "print"
    ONLINE = "online"
    SOCIAL_MEDIA = "social_media"


class UsageType(Enum):
    """Types of licensed content usage"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SYNC = "sync"
    PERFORMANCE = "performance"
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    BROADCAST = "broadcast"
    PODCAST = "podcast"
    ADVERTISING = "advertising"
    BACKGROUND_MUSIC = "background_music"
    RINGTONE = "ringtone"
    REMIX = "remix"


class LicenseStatus(Enum):
    """Status of license agreements"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    RENEWED = "renewed"
    DISPUTED = "disputed"
    UNDER_REVIEW = "under_review"


class PaymentStructure(Enum):
    """Payment structures for licensing"""
    FLAT_FEE = "flat_fee"
    ROYALTY = "royalty"
    REVENUE_SHARE = "revenue_share"
    HYBRID = "hybrid"
    PER_USE = "per_use"
    SUBSCRIPTION = "subscription"
    TIERED = "tiered"
    DYNAMIC_PRICING = "dynamic_pricing"
    AUCTION = "auction"
    PERFORMANCE_BASED = "performance_based"


# ============================================================================
# REVENUE MODELS
# ============================================================================

class RevenueModel(Base):
    """
    Enterprise revenue model for comprehensive revenue tracking and optimization.
    Multi-source revenue management with real-time analytics and forecasting.
    """
    __tablename__ = 'revenue'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=True, index=True)
    
    # Revenue classification
    revenue_source = Column(SQLEnum(RevenueSource), nullable=False, index=True)
    status = Column(SQLEnum(RevenueStatus), nullable=False, default=RevenueStatus.PENDING, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True, index=True)
    period = Column(SQLEnum(RevenuePeriod), nullable=False, default=RevenuePeriod.MONTHLY, index=True)
    
    # Financial data (using Decimal for precision)
    gross_amount = Column(Numeric(15, 4), nullable=False)  # Precise decimal for money
    net_amount = Column(Numeric(15, 4), nullable=False)
    platform_fee = Column(Numeric(15, 4), default=0)
    processing_fee = Column(Numeric(15, 4), default=0)
    tax_amount = Column(Numeric(15, 4), default=0)
    currency = Column(String(3), nullable=False, default="USD", index=True)  # ISO currency code
    
    # Exchange rate data
    original_currency = Column(String(3))
    original_amount = Column(Numeric(15, 4))
    exchange_rate = Column(Numeric(10, 6))
    exchange_rate_timestamp = Column(DateTime(timezone=True))
    
    # Platform & source details
    platform = Column(String(100), index=True)  # "youtube", "spotify", "instagram"
    platform_transaction_id = Column(String(200), unique=True, index=True)
    platform_payout_id = Column(String(200))
    external_reference = Column(String(200))
    
    # Performance metrics
    views_at_payment = Column(Integer, default=0)
    engagement_rate_at_payment = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)  # views to revenue conversion
    rpm = Column(Float, default=0.0)  # Revenue per mille (thousand views)
    cpm = Column(Float, default=0.0)  # Cost per mille
    
    # Geographic data
    country = Column(String(10))  # ISO country code
    region = Column(String(100))
    tax_jurisdiction = Column(String(100))
    tax_rate = Column(Float, default=0.0)
    
    # Time tracking
    earned_date = Column(DateTime(timezone=True), nullable=False, index=True)
    payment_date = Column(DateTime(timezone=True), index=True)
    due_date = Column(DateTime(timezone=True))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Analytics & forecasting
    predicted_amount = Column(Numeric(15, 4))
    forecast_confidence = Column(Float, default=0.0)  # 0-1 confidence in prediction
    seasonal_factor = Column(Float, default=1.0)
    trend_factor = Column(Float, default=1.0)
    growth_rate = Column(Float, default=0.0)
    
    # Audience demographics (for targeted revenue optimization)
    audience_age_group = Column(String(20))  # "18-24", "25-34", etc.
    audience_gender_split = Column(JSONB, default=dict)  # {"male": 60, "female": 40}
    audience_top_countries = Column(JSONB, default=list)  # ["US", "DE", "FR"]
    audience_interests = Column(JSONB, default=list)
    
    # Revenue optimization
    optimization_applied = Column(Boolean, default=False)
    optimization_type = Column(String(100))
    optimization_impact = Column(Float, default=0.0)  # % improvement
    a_b_test_variant = Column(String(50))
    
    # Licensing & Rights
    license_id = Column(UUID(as_uuid=True), ForeignKey('licensing.id'), nullable=True)
    royalty_rate = Column(Float, default=0.0)  # Percentage
    rights_holder_share = Column(Float, default=100.0)  # Percentage
    collaborator_shares = Column(JSONB, default=dict)  # {"user_id": percentage}
    
    # Payment processing
    payment_processor = Column(String(100))
    payment_processor_fee = Column(Numeric(15, 4), default=0)
    payout_batch_id = Column(String(200))
    reconciliation_status = Column(String(50), default="pending")
    
    # Quality & Validation
    data_quality_score = Column(Float, default=1.0)  # 0-1 data quality
    verification_status = Column(String(20), default="verified")
    anomaly_detected = Column(Boolean, default=False)
    manual_review_required = Column(Boolean, default=False)
    
    # Compliance & Reporting
    tax_reporting_required = Column(Boolean, default=True)
    tax_form_type = Column(String(20))  # "1099", "1042-S", etc.
    compliance_status = Column(String(50), default="compliant")
    audit_trail = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    reconciled_at = Column(DateTime(timezone=True))
    
    # System flags
    is_recurring = Column(Boolean, default=False)
    is_disputed = Column(Boolean, default=False, index=True)
    is_refunded = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="revenue_records")
    content = relationship("ContentModel", backref="revenue_records")
    license_agreement = relationship("LicensingModel", back_populates="revenue_records")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_revenue_user_earned', 'user_id', 'earned_date'),
        Index('idx_revenue_platform_status', 'platform', 'status'),
        Index('idx_revenue_source_currency', 'revenue_source', 'currency'),
        Index('idx_revenue_period_amount', 'period', 'gross_amount'),
        Index('idx_revenue_country_tax', 'country', 'tax_jurisdiction'),
    )
    
    def __repr__(self):
        return f"<RevenueModel(id={self.id}, amount={self.gross_amount} {self.currency}, source={self.revenue_source.value})>"


# ============================================================================
# LICENSING MODELS
# ============================================================================

class LicensingModel(Base):
    """
    Enterprise licensing model for automated license management and compliance.
    Comprehensive licensing system with contract generation and royalty tracking.
    """
    __tablename__ = 'licensing'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False, index=True)
    licensor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)  # Content owner
    licensee_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)  # License buyer
    
    # License classification
    license_type = Column(SQLEnum(LicenseType), nullable=False, index=True)
    license_category = Column(SQLEnum(LicenseCategory), nullable=False, index=True)
    usage_type = Column(SQLEnum(UsageType), nullable=False, index=True)
    status = Column(SQLEnum(LicenseStatus), nullable=False, default=LicenseStatus.DRAFT, index=True)
    payment_structure = Column(SQLEnum(PaymentStructure), nullable=False, index=True)
    
    # License identification
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    contract_version = Column(String(20), default="1.0")
    template_id = Column(String(100))
    custom_terms_applied = Column(Boolean, default=False)
    
    # Financial terms
    base_price = Column(Numeric(15, 4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    royalty_rate = Column(Float, default=0.0)  # Percentage for ongoing royalties
    minimum_guarantee = Column(Numeric(15, 4), default=0)
    advance_payment = Column(Numeric(15, 4), default=0)
    
    # Payment terms
    payment_schedule = Column(String(50), default="upfront")  # "upfront", "monthly", "quarterly"
    payment_due_days = Column(Integer, default=30)
    late_payment_fee_rate = Column(Float, default=0.0)
    currency_hedging = Column(Boolean, default=False)
    
    # Usage terms
    usage_territory = Column(JSONB, default=list)  # ["US", "CA", "global"]
    usage_duration_months = Column(Integer)  # null = perpetual
    usage_start_date = Column(DateTime(timezone=True))
    usage_end_date = Column(DateTime(timezone=True))
    usage_limitations = Column(JSONB, default=dict)
    
    # Rights & Restrictions
    exclusive = Column(Boolean, default=False)
    transferable = Column(Boolean, default=False)
    sublicense_allowed = Column(Boolean, default=False)
    modification_allowed = Column(Boolean, default=False)
    commercial_use = Column(Boolean, default=True)
    
    # Usage tracking
    max_usage_count = Column(Integer)  # null = unlimited
    current_usage_count = Column(Integer, default=0)
    max_audience_size = Column(Integer)  # Maximum audience reach
    max_revenue_cap = Column(Numeric(15, 4))  # Revenue cap before renegotiation
    
    # Performance metrics
    total_revenue_generated = Column(Numeric(15, 4), default=0)
    total_royalties_paid = Column(Numeric(15, 4), default=0)
    total_usage_instances = Column(Integer, default=0)
    performance_bonus_earned = Column(Numeric(15, 4), default=0)
    
    # Legal & Compliance
    governing_law = Column(String(100), default="United States")
    dispute_resolution = Column(String(100), default="arbitration")
    termination_notice_days = Column(Integer, default=30)
    force_majeure_clause = Column(Boolean, default=True)
    indemnification_clause = Column(Boolean, default=True)
    
    # Contract details
    contract_signed_date = Column(DateTime(timezone=True))
    contract_effective_date = Column(DateTime(timezone=True))
    contract_expiration_date = Column(DateTime(timezone=True))
    auto_renewal = Column(Boolean, default=False)
    renewal_notice_days = Column(Integer, default=60)
    
    # Digital signature & verification
    licensor_signature = Column(String(500))  # Digital signature
    licensee_signature = Column(String(500))
    signature_timestamp = Column(DateTime(timezone=True))
    ip_address_signature = Column(String(50))
    verification_hash = Column(String(200))
    
    # Communication & Updates
    communication_log = Column(JSONB, default=list)
    amendment_history = Column(JSONB, default=list)
    renewal_notifications_sent = Column(Integer, default=0)
    last_communication = Column(DateTime(timezone=True))
    
    # Monitoring & Compliance
    compliance_checks = Column(JSONB, default=dict)
    violation_detected = Column(Boolean, default=False)
    violation_details = Column(Text)
    last_compliance_check = Column(DateTime(timezone=True))
    
    # Performance & Analytics
    market_value = Column(Numeric(15, 4))  # Current market value of license
    price_elasticity = Column(Float, default=1.0)
    demand_score = Column(Float, default=0.0)  # 0-1 demand rating
    competition_analysis = Column(JSONB, default=dict)
    
    # AI & Automation
    ai_terms_generated = Column(Boolean, default=False)
    ai_optimization_applied = Column(Boolean, default=False)
    ai_risk_assessment = Column(Float, default=0.0)  # 0-1 risk score
    ai_pricing_suggested = Column(Numeric(15, 4))
    
    # Reporting & Analytics
    usage_analytics = Column(JSONB, default=dict)
    revenue_forecasting = Column(JSONB, default=dict)
    performance_metrics = Column(JSONB, default=dict)
    roi_calculation = Column(Float, default=0.0)
    
    # Third-party integrations
    crm_integration_id = Column(String(200))
    accounting_integration_id = Column(String(200))
    legal_platform_id = Column(String(200))
    blockchain_record_hash = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_payment_date = Column(DateTime(timezone=True))
    next_payment_due = Column(DateTime(timezone=True))
    
    # System flags
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    is_disputed = Column(Boolean, default=False)
    is_terminated = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    content = relationship("ContentModel", backref="licenses")
    licensor = relationship("UserModel", foreign_keys=[licensor_id], backref="licenses_granted")
    licensee = relationship("UserModel", foreign_keys=[licensee_id], backref="licenses_acquired")
    revenue_records = relationship("RevenueModel", back_populates="license_agreement", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_license_content_status', 'content_id', 'status'),
        Index('idx_license_licensor_type', 'licensor_id', 'license_type'),
        Index('idx_license_licensee_category', 'licensee_id', 'license_category'),
        Index('idx_license_effective_expiration', 'contract_effective_date', 'contract_expiration_date'),
        Index('idx_license_revenue_exclusive', 'total_revenue_generated', 'exclusive'),
    )
    
    def __repr__(self):
        return f"<LicensingModel(id={self.id}, type={self.license_type.value}, price={self.base_price} {self.currency})>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_revenue_example(user_id: str, content_id: str = None, 
                         amount: float = 100.0, source: RevenueSource = RevenueSource.ADS) -> RevenueModel:
    """Create example revenue record for testing and development"""
    return RevenueModel(
        user_id=user_id,
        content_id=content_id,
        revenue_source=source,
        gross_amount=Decimal(str(amount)),
        net_amount=Decimal(str(amount * 0.85)),  # 15% platform fee
        platform_fee=Decimal(str(amount * 0.15)),
        currency="USD",
        platform="youtube",
        earned_date=datetime.utcnow()
    )


def create_licensing_example(content_id: str, licensor_id: str, 
                           license_type: LicenseType = LicenseType.NON_EXCLUSIVE,
                           price: float = 500.0) -> LicensingModel:
    """Create example license agreement for testing and development"""
    return LicensingModel(
        content_id=content_id,
        licensor_id=licensor_id,
        license_type=license_type,
        license_category=LicenseCategory.COMMERCIAL,
        usage_type=UsageType.STREAMING,
        payment_structure=PaymentStructure.FLAT_FEE,
        license_number=f"LIC-{uuid.uuid4().hex[:8].upper()}",
        base_price=Decimal(str(price)),
        currency="USD",
        usage_territory=["global"],
        commercial_use=True
    )


def calculate_royalty_payment(license: LicensingModel, revenue_amount: float) -> float:
    """Calculate royalty payment based on license terms"""
    if license.royalty_rate > 0:
        return revenue_amount * (license.royalty_rate / 100.0)
    return 0.0


def calculate_license_value(license: LicensingModel, market_factors: Dict[str, float] = None) -> float:
    """Calculate current market value of a license"""
    base_value = float(license.base_price)
    
    if market_factors:
        # Apply market factors
        demand_multiplier = market_factors.get('demand', 1.0)
        scarcity_multiplier = market_factors.get('scarcity', 1.0)
        performance_multiplier = market_factors.get('performance', 1.0)
        
        market_value = base_value * demand_multiplier * scarcity_multiplier * performance_multiplier
        return market_value
    
    return base_value


def estimate_revenue_forecast(historical_data: List[RevenueModel], 
                            periods_ahead: int = 12) -> List[Dict[str, Any]]:
    """Estimate revenue forecast based on historical data"""
    if not historical_data:
        return []
    
    # Simple trend-based forecast (in production, use more sophisticated ML models)
    recent_revenues = [float(record.gross_amount) for record in historical_data[-6:]]
    average_revenue = sum(recent_revenues) / len(recent_revenues)
    
    # Calculate trend
    if len(recent_revenues) > 1:
        trend = (recent_revenues[-1] - recent_revenues[0]) / len(recent_revenues)
    else:
        trend = 0
    
    forecast = []
    for i in range(periods_ahead):
        projected_amount = average_revenue + (trend * i)
        confidence = max(0.1, 1.0 - (i * 0.1))  # Decreasing confidence over time
        
        forecast.append({
            'period': i + 1,
            'projected_amount': round(projected_amount, 2),
            'confidence': round(confidence, 2),
            'currency': historical_data[-1].currency if historical_data else 'USD'
        })
    
    return forecast


# ============================================================================
# EXPORT SECTION
# ============================================================================

__all__ = [
    # Models
    'RevenueModel', 'LicensingModel',
    
    # Revenue Enums
    'RevenueSource', 'RevenueStatus', 'PaymentMethod', 'RevenuePeriod',
    
    # Licensing Enums
    'LicenseType', 'LicenseCategory', 'UsageType', 'LicenseStatus', 'PaymentStructure',
    
    # Utility Functions
    'create_revenue_example', 'create_licensing_example',
    'calculate_royalty_payment', 'calculate_license_value', 'estimate_revenue_forecast'
]