"""Revenue Tracking Database Model

Enterprise-grade SQLAlchemy model for revenue tracking, monetization analytics,
and financial performance monitoring across multiple platforms.

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


class RevenueType(Enum):
    """Revenue type enumeration"""    STREAMING_ROYALTIES = "streaming_royalties"
    DOWNLOAD_SALES = "download_sales"
    LICENSING_FEES = "licensing_fees"
    SYNC_LICENSING = "sync_licensing"
    PERFORMANCE_ROYALTIES = "performance_royalties"
    MECHANICAL_ROYALTIES = "mechanical_royalties"
    MERCHANDISING = "merchandising"
    SPONSORSHIP = "sponsorship"
    AFFILIATE_COMMISSION = "affiliate_commission"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_MONETIZATION = "content_monetization"
    COPYRIGHT_CLAIMS = "copyright_claims"
    RECOVERED_REVENUE = "recovered_revenue"


class Currency(Enum):
    """Supported currencies"""    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"
    HUF = "HUF"
    RON = "RON"
    BGN = "BGN"
    HRK = "HRK"


class Platform(Enum):
    """Revenue platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    DIRECT_SALES = "direct_sales"
    LICENSING_AGENCY = "licensing_agency"
    PERFORMANCE_SOCIETY = "performance_society"
    OTHER = "other"


class PaymentStatus(Enum):
    """Payment processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"
    REQUIRES_VERIFICATION = "requires_verification"


class RevenueStatus(Enum):
    """Revenue record status"""    DRAFT = "draft"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    VERIFIED = "verified"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class TaxStatus(Enum):
    """Tax processing status"""    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    CALCULATED = "calculated"
    PAID = "paid"
    EXEMPT = "exempt"
    DISPUTED = "disputed"


class RevenueTracking(Base):
    """    Enterprise Revenue Tracking Model
    
    Comprehensive revenue tracking system for content monetization across
    multiple platforms with advanced analytics, tax management, and payout automation.
    """    __tablename__ = "revenue_tracking"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Revenue classification
    revenue_type = Column(SQLEnum(RevenueType), nullable=False, index=True)
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    revenue_status = Column(SQLEnum(RevenueStatus), default=RevenueStatus.CONFIRMED, index=True)
    
    # Financial data
    gross_amount = Column(Numeric(15, 4), nullable=False)  # High precision for financial data
    net_amount = Column(Numeric(15, 4), nullable=False)
    currency = Column(SQLEnum(Currency), default=Currency.EUR, nullable=False)
    exchange_rate = Column(Numeric(10, 6), default=1.0)  # Exchange rate to base currency
    base_currency_amount = Column(Numeric(15, 4), nullable=True)  # Amount in base currency
    
    # Platform fees and deductions
    platform_fee = Column(Numeric(15, 4), default=0.0)
    platform_fee_percentage = Column(Float, default=0.0)
    service_fee = Column(Numeric(15, 4), default=0.0)
    processing_fee = Column(Numeric(15, 4), default=0.0)
    other_deductions = Column(Numeric(15, 4), default=0.0)
    deduction_details = Column(JSON, nullable=True)
    
    # Tax information
    tax_status = Column(SQLEnum(TaxStatus), default=TaxStatus.NOT_APPLICABLE)
    tax_amount = Column(Numeric(15, 4), default=0.0)
    tax_percentage = Column(Float, default=0.0)
    tax_jurisdiction = Column(String(100), nullable=True)
    tax_reference = Column(String(255), nullable=True)
    vat_amount = Column(Numeric(15, 4), default=0.0)
    vat_percentage = Column(Float, default=0.0)
    
    # Time periods
    revenue_period_start = Column(DateTime(timezone=True), nullable=False)
    revenue_period_end = Column(DateTime(timezone=True), nullable=False)
    reporting_date = Column(DateTime(timezone=True), nullable=False)
    payment_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Content and performance metrics
    content_title = Column(String(500), nullable=True)
    content_description = Column(Text, nullable=True)
    content_duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Performance metrics
    play_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # Geographic data
    revenue_by_country = Column(JSON, nullable=True)
    top_countries = Column(ARRAY(String), nullable=True)
    geographic_distribution = Column(JSON, nullable=True)
    
    # Audience analytics
    audience_age_groups = Column(JSON, nullable=True)
    audience_gender_split = Column(JSON, nullable=True)
    audience_interests = Column(JSON, nullable=True)
    listening_behavior = Column(JSON, nullable=True)
    
    # Platform-specific data
    platform_content_id = Column(String(255), nullable=True)
    platform_artist_id = Column(String(255), nullable=True)
    platform_metrics = Column(JSON, nullable=True)
    platform_raw_data = Column(JSON, nullable=True)
    
    # Payment information
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(100), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    payment_processor = Column(String(100), nullable=True)
    payout_amount = Column(Numeric(15, 4), nullable=True)
    payout_date = Column(DateTime(timezone=True), nullable=True)
    payout_reference = Column(String(255), nullable=True)
    
    # Collaboration and revenue sharing
    collaborators = Column(JSON, nullable=True)
    revenue_splits = Column(JSON, nullable=True)
    royalty_shares = Column(JSON, nullable=True)
    split_payments = Column(JSON, nullable=True)
    
    # Contract and licensing
    contract_id = Column(String(255), nullable=True)
    licensing_agreement_id = Column(UUID(as_uuid=True), ForeignKey('licensing_agreements.id'), nullable=True)
    royalty_rate = Column(Float, nullable=True)
    minimum_guarantee = Column(Numeric(15, 4), nullable=True)
    advance_amount = Column(Numeric(15, 4), nullable=True)
    recoupment_status = Column(String(50), nullable=True)
    
    # Analytics and predictions
    revenue_trend = Column(JSON, nullable=True)
    growth_rate = Column(Float, nullable=True)
    projected_revenue = Column(Numeric(15, 4), nullable=True)
    market_performance = Column(JSON, nullable=True)
    competitive_analysis = Column(JSON, nullable=True)
    
    # Machine learning insights
    ml_revenue_prediction = Column(Numeric(15, 4), nullable=True)
    ml_confidence_score = Column(Float, nullable=True)
    ml_factors = Column(JSON, nullable=True)
    anomaly_score = Column(Float, default=0.0)
    
    # Quality and validation
    data_quality_score = Column(Float, default=1.0)
    validation_status = Column(String(50), default="validated")
    data_source_reliability = Column(Float, default=1.0)
    manual_verification = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    synced_at = Column(DateTime(timezone=True), nullable=True)
    next_sync_due = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_disputed = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    is_automated = Column(Boolean, default=True)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="revenue_records")
    licensing_agreement = relationship("LicensingAgreement", back_populates="revenue_records")
    audit_logs = relationship("AuditLog", back_populates="revenue_tracking", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_revenue_user_platform', 'user_id', 'platform'),
        Index('idx_revenue_period', 'revenue_period_start', 'revenue_period_end'),
        Index('idx_revenue_type_status', 'revenue_type', 'revenue_status'),
        Index('idx_revenue_payment_status', 'payment_status', 'payment_due_date'),
        Index('idx_revenue_amount_currency', 'gross_amount', 'currency'),
        Index('idx_revenue_platform_date', 'platform', 'reporting_date'),
        Index('idx_revenue_content_fingerprint', 'content_fingerprint_id', 'revenue_type'),
        Index('idx_revenue_performance_metrics', 'play_count', 'view_count'),
        Index('idx_revenue_verification', 'is_verified', 'requires_review'),
    )
    
    def __repr__(self):
        return f"<RevenueTracking(id={self.id}, platform={self.platform.value}, revenue_type={self.revenue_type.value}, amount={self.gross_amount})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""        return {
            "id": str(self.id),
            "content_fingerprint_id": str(self.content_fingerprint_id) if self.content_fingerprint_id else None,
            "user_id": str(self.user_id),
            "revenue_type": self.revenue_type.value if self.revenue_type else None,
            "platform": self.platform.value if self.platform else None,
            "revenue_status": self.revenue_status.value if self.revenue_status else None,
            "gross_amount": float(self.gross_amount),
            "net_amount": float(self.net_amount),
            "currency": self.currency.value if self.currency else None,
            "exchange_rate": float(self.exchange_rate) if self.exchange_rate else None,
            "base_currency_amount": float(self.base_currency_amount) if self.base_currency_amount else None,
            "platform_fee": float(self.platform_fee),
            "platform_fee_percentage": self.platform_fee_percentage,
            "service_fee": float(self.service_fee),
            "processing_fee": float(self.processing_fee),
            "other_deductions": float(self.other_deductions),
            "deduction_details": self.deduction_details,
            "tax_status": self.tax_status.value if self.tax_status else None,
            "tax_amount": float(self.tax_amount),
            "tax_percentage": self.tax_percentage,
            "tax_jurisdiction": self.tax_jurisdiction,
            "tax_reference": self.tax_reference,
            "vat_amount": float(self.vat_amount),
            "vat_percentage": self.vat_percentage,
            "revenue_period_start": self.revenue_period_start.isoformat() if self.revenue_period_start else None,
            "revenue_period_end": self.revenue_period_end.isoformat() if self.revenue_period_end else None,
            "reporting_date": self.reporting_date.isoformat() if self.reporting_date else None,
            "payment_due_date": self.payment_due_date.isoformat() if self.payment_due_date else None,
            "content_title": self.content_title,
            "content_description": self.content_description,
            "content_duration": self.content_duration,
            "play_count": self.play_count,
            "download_count": self.download_count,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "revenue_by_country": self.revenue_by_country,
            "top_countries": self.top_countries,
            "geographic_distribution": self.geographic_distribution,
            "audience_age_groups": self.audience_age_groups,
            "audience_gender_split": self.audience_gender_split,
            "audience_interests": self.audience_interests,
            "listening_behavior": self.listening_behavior,
            "platform_content_id": self.platform_content_id,
            "platform_artist_id": self.platform_artist_id,
            "platform_metrics": self.platform_metrics,
            "payment_status": self.payment_status.value if self.payment_status else None,
            "payment_method": self.payment_method,
            "payment_reference": self.payment_reference,
            "payment_processor": self.payment_processor,
            "payout_amount": float(self.payout_amount) if self.payout_amount else None,
            "payout_date": self.payout_date.isoformat() if self.payout_date else None,
            "payout_reference": self.payout_reference,
            "collaborators": self.collaborators,
            "revenue_splits": self.revenue_splits,
            "royalty_shares": self.royalty_shares,
            "split_payments": self.split_payments,
            "contract_id": self.contract_id,
            "licensing_agreement_id": str(self.licensing_agreement_id) if self.licensing_agreement_id else None,
            "royalty_rate": self.royalty_rate,
            "minimum_guarantee": float(self.minimum_guarantee) if self.minimum_guarantee else None,
            "advance_amount": float(self.advance_amount) if self.advance_amount else None,
            "recoupment_status": self.recoupment_status,
            "revenue_trend": self.revenue_trend,
            "growth_rate": self.growth_rate,
            "projected_revenue": float(self.projected_revenue) if self.projected_revenue else None,
            "market_performance": self.market_performance,
            "competitive_analysis": self.competitive_analysis,
            "ml_revenue_prediction": float(self.ml_revenue_prediction) if self.ml_revenue_prediction else None,
            "ml_confidence_score": self.ml_confidence_score,
            "ml_factors": self.ml_factors,
            "anomaly_score": self.anomaly_score,
            "data_quality_score": self.data_quality_score,
            "validation_status": self.validation_status,
            "data_source_reliability": self.data_source_reliability,
            "manual_verification": self.manual_verification,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "next_sync_due": self.next_sync_due.isoformat() if self.next_sync_due else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_disputed": self.is_disputed,
            "requires_review": self.requires_review,
            "is_automated": self.is_automated
        }
    
    def calculate_net_revenue(self) -> Decimal:
        """Calculate net revenue after all deductions"""        total_deductions = (
            self.platform_fee + 
            self.service_fee + 
            self.processing_fee + 
            self.other_deductions + 
            self.tax_amount + 
            self.vat_amount
        )
        return self.gross_amount - total_deductions
    
    def calculate_profit_margin(self) -> float:
        """Calculate profit margin percentage"""        if self.gross_amount > 0:
            return float((self.net_amount / self.gross_amount) * 100)
        return 0.0
    
    def get_effective_royalty_rate(self) -> float:
        """Get effective royalty rate based on performance"""        if self.play_count and self.gross_amount:
            return float(self.gross_amount / self.play_count)
        return self.royalty_rate or 0.0
    
    def is_payment_overdue(self) -> bool:
        """Check if payment is overdue"""        if self.payment_due_date and self.payment_status == PaymentStatus.PENDING:
            return datetime.now(timezone.utc) > self.payment_due_date
        return False
    
    @classmethod
    def create_from_platform_data(cls, platform_data: Dict[str, Any], user_id: str, content_fingerprint_id: str = None) -> 'RevenueTracking':
        """Create RevenueTracking from platform API data"""        return cls(
            content_fingerprint_id=content_fingerprint_id,
            user_id=user_id,
            revenue_type=RevenueType(platform_data.get('revenue_type', 'streaming_royalties')),
            platform=Platform(platform_data.get('platform', 'spotify')),
            gross_amount=Decimal(str(platform_data.get('gross_amount', 0.0))),
            net_amount=Decimal(str(platform_data.get('net_amount', 0.0))),
            currency=Currency(platform_data.get('currency', 'EUR')),
            platform_fee=Decimal(str(platform_data.get('platform_fee', 0.0))),
            platform_fee_percentage=platform_data.get('platform_fee_percentage', 0.0),
            revenue_period_start=platform_data.get('period_start'),
            revenue_period_end=platform_data.get('period_end'),
            reporting_date=platform_data.get('reporting_date', datetime.now(timezone.utc)),
            content_title=platform_data.get('content_title'),
            platform_content_id=platform_data.get('platform_content_id'),
            play_count=platform_data.get('play_count', 0),
            platform_metrics=platform_data.get('platform_metrics', {}),
            platform_raw_data=platform_data.get('raw_data', {})
        )
