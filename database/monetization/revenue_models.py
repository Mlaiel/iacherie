"""Revenue Models - Enterprise Database Models for Revenue Tracking

Ultra-advanced SQLAlchemy models for comprehensive revenue tracking across all platforms
and content types with advanced analytics and financial management capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, 
    ForeignKey, Index, Enum as SQLEnum, Numeric, UniqueConstraint,
    CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union

Base = declarative_base()


class RevenueType(Enum):
    """Comprehensive revenue stream types for content creators"""    # Streaming revenue
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    PODCAST_STREAMING = "podcast_streaming"
    LIVE_STREAMING = "live_streaming"
    
    # Digital sales
    TRACK_PURCHASE = "track_purchase"
    ALBUM_PURCHASE = "album_purchase"
    VIDEO_PURCHASE = "video_purchase"
    DIGITAL_DOWNLOAD = "digital_download"
    
    # Licensing and rights
    SYNC_LICENSING = "sync_licensing"
    MECHANICAL_ROYALTIES = "mechanical_royalties"
    PERFORMANCE_ROYALTIES = "performance_royalties"
    MASTER_RECORDING_ROYALTIES = "master_recording_royalties"
    PUBLISHING_ROYALTIES = "publishing_royalties"
    NEIGHBORING_RIGHTS = "neighboring_rights"
    
    # Brand and partnership
    BRAND_SPONSORSHIP = "brand_sponsorship"
    AFFILIATE_MARKETING = "affiliate_marketing"
    PRODUCT_PLACEMENT = "product_placement"
    ENDORSEMENT_DEALS = "endorsement_deals"
    
    # Content monetization
    AD_REVENUE = "ad_revenue"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    PREMIUM_CONTENT = "premium_content"
    PAY_PER_VIEW = "pay_per_view"
    TIPS_DONATIONS = "tips_donations"
    
    # Merchandise and physical
    MERCHANDISE_SALES = "merchandise_sales"
    VINYL_SALES = "vinyl_sales"
    CD_SALES = "cd_sales"
    PHYSICAL_MEDIA = "physical_media"
    
    # Live and events
    CONCERT_REVENUE = "concert_revenue"
    EVENT_APPEARANCE = "event_appearance"
    VIRTUAL_EVENTS = "virtual_events"
    WORKSHOP_REVENUE = "workshop_revenue"
    
    # Digital assets
    NFT_SALES = "nft_sales"
    BLOCKCHAIN_ROYALTIES = "blockchain_royalties"
    CRYPTOCURRENCY_PAYMENTS = "cryptocurrency_payments"
    
    # Collaboration
    COLLABORATION_SPLITS = "collaboration_splits"
    REMIX_ROYALTIES = "remix_royalties"
    FEATURE_PAYMENTS = "feature_payments"
    
    # Recovery and protection
    COPYRIGHT_CLAIMS = "copyright_claims"
    RECOVERED_REVENUE = "recovered_revenue"
    INFRINGEMENT_SETTLEMENTS = "infringement_settlements"
    
    # Other
    CROWDFUNDING = "crowdfunding"
    GRANTS = "grants"
    CONTEST_WINNINGS = "contest_winnings"
    OTHER = "other"


class PlatformType(Enum):
    """Comprehensive platform types for revenue generation"""    # Music platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    YOUTUBE_MUSIC = "youtube_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    AUDIOMACK = "audiomack"
    PANDORA = "pandora"
    
    # Video platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    
    # Social and content
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    
    # Subscription and fan platforms
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    KOFI = "kofi"
    BUYMEACOFFEE = "buymeacoffee"
    FANVUE = "fanvue"
    
    # Podcast platforms
    SPOTIFY_PODCASTS = "spotify_podcasts"
    APPLE_PODCASTS = "apple_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    ANCHOR = "anchor"
    CASTBOX = "castbox"
    
    # E-commerce and marketplaces
    ETSY = "etsy"
    AMAZON = "amazon"
    EBAY = "ebay"
    SHOPIFY = "shopify"
    GUMROAD = "gumroad"
    
    # Blockchain and crypto
    OPENSEA = "opensea"
    FOUNDATION = "foundation"
    SUPERRARE = "superrare"
    ASYNC_ART = "async_art"
    
    # Direct and misc
    DIRECT_SALES = "direct_sales"
    LICENSING_AGENCIES = "licensing_agencies"
    PERFORMANCE_SOCIETIES = "performance_societies"
    DISTRIBUTION_SERVICES = "distribution_services"
    OTHER = "other"


class Currency(Enum):
    """Supported currencies for international revenue tracking"""    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    SEK = "SEK"  # Swedish Krona
    NOK = "NOK"  # Norwegian Krone
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    CZK = "CZK"  # Czech Koruna
    HUF = "HUF"  # Hungarian Forint
    RON = "RON"  # Romanian Leu
    BGN = "BGN"  # Bulgarian Lev
    HRK = "HRK"  # Croatian Kuna
    RUB = "RUB"  # Russian Ruble
    CNY = "CNY"  # Chinese Yuan
    KRW = "KRW"  # South Korean Won
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    MXN = "MXN"  # Mexican Peso
    ARS = "ARS"  # Argentine Peso
    CLP = "CLP"  # Chilean Peso
    COP = "COP"  # Colombian Peso
    PEN = "PEN"  # Peruvian Sol
    ZAR = "ZAR"  # South African Rand
    EGP = "EGP"  # Egyptian Pound
    TRY = "TRY"  # Turkish Lira
    ILS = "ILS"  # Israeli Shekel
    AED = "AED"  # UAE Dirham
    SAR = "SAR"  # Saudi Riyal
    THB = "THB"  # Thai Baht
    SGD = "SGD"  # Singapore Dollar
    MYR = "MYR"  # Malaysian Ringgit
    IDR = "IDR"  # Indonesian Rupiah
    VND = "VND"  # Vietnamese Dong
    PHP = "PHP"  # Philippine Peso
    
    # Cryptocurrencies
    BTC = "BTC"   # Bitcoin
    ETH = "ETH"   # Ethereum
    USDC = "USDC" # USD Coin
    USDT = "USDT" # Tether
    BNB = "BNB"   # Binance Coin


class RevenueStatus(Enum):
    """Revenue record status lifecycle"""    PENDING = "pending"
    ESTIMATED = "estimated"
    CONFIRMED = "confirmed"
    VERIFIED = "verified"
    PROCESSED = "processed"
    PAID = "paid"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    ARCHIVED = "archived"


class PaymentStatus(Enum):
    """Payment processing status"""    PENDING_APPROVAL = "pending_approval"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"
    REQUIRES_VERIFICATION = "requires_verification"
    AWAITING_THRESHOLD = "awaiting_threshold"


class TaxStatus(Enum):
    """Tax processing and compliance status"""    NOT_APPLICABLE = "not_applicable"
    PENDING_CALCULATION = "pending_calculation"
    CALCULATED = "calculated"
    DEDUCTED = "deducted"
    PAID = "paid"
    EXEMPT = "exempt"
    DISPUTED = "disputed"
    REQUIRES_DOCUMENTATION = "requires_documentation"


class RevenueRecord(Base):
    """    Enterprise Revenue Record Model
    
    Core model for tracking individual revenue transactions with comprehensive
    metadata, performance analytics, and financial management capabilities.
    """    __tablename__ = "revenue_records"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_transaction_id = Column(String(255), nullable=True, index=True)
    
    # User and content associations
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_requests.id'), nullable=True, index=True)
    
    # Revenue classification
    revenue_type = Column(SQLEnum(RevenueType), nullable=False, index=True)
    platform = Column(SQLEnum(PlatformType), nullable=False, index=True)
    revenue_status = Column(SQLEnum(RevenueStatus), default=RevenueStatus.PENDING, index=True)
    
    # Financial data (high precision for accuracy)
    gross_amount = Column(Numeric(18, 6), nullable=False)
    net_amount = Column(Numeric(18, 6), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    exchange_rate = Column(Numeric(12, 8), default=1.0)
    base_currency_amount = Column(Numeric(18, 6), nullable=True)
    base_currency = Column(SQLEnum(Currency), default=Currency.EUR)
    
    # Platform fees and deductions
    platform_fee = Column(Numeric(18, 6), default=0.0)
    platform_fee_percentage = Column(Numeric(8, 4), default=0.0)
    service_fee = Column(Numeric(18, 6), default=0.0)
    processing_fee = Column(Numeric(18, 6), default=0.0)
    distribution_fee = Column(Numeric(18, 6), default=0.0)
    transaction_fee = Column(Numeric(18, 6), default=0.0)
    other_deductions = Column(Numeric(18, 6), default=0.0)
    deduction_breakdown = Column(JSONB, nullable=True)
    
    # Tax and legal compliance
    tax_status = Column(SQLEnum(TaxStatus), default=TaxStatus.NOT_APPLICABLE)
    gross_tax_amount = Column(Numeric(18, 6), default=0.0)
    income_tax_amount = Column(Numeric(18, 6), default=0.0)
    vat_amount = Column(Numeric(18, 6), default=0.0)
    withholding_tax = Column(Numeric(18, 6), default=0.0)
    tax_rate_applied = Column(Numeric(8, 4), default=0.0)
    tax_jurisdiction = Column(String(100), nullable=True)
    tax_year = Column(Integer, nullable=True)
    tax_document_reference = Column(String(255), nullable=True)
    
    # Time tracking
    revenue_period_start = Column(DateTime(timezone=True), nullable=False)
    revenue_period_end = Column(DateTime(timezone=True), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    reporting_date = Column(DateTime(timezone=True), nullable=False)
    payment_due_date = Column(DateTime(timezone=True), nullable=True)
    payment_received_date = Column(DateTime(timezone=True), nullable=True)
    
    # Content metadata
    content_title = Column(String(500), nullable=True)
    content_description = Column(Text, nullable=True)
    content_type = Column(String(100), nullable=True)  # audio, video, image, text
    content_duration = Column(Float, nullable=True)  # Duration in seconds
    content_size_bytes = Column(Integer, nullable=True)
    content_quality = Column(String(50), nullable=True)  # HD, 4K, lossless, etc.
    
    # Performance metrics
    play_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    stream_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    playlist_additions = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Geographic and demographic data
    revenue_by_country = Column(JSONB, nullable=True)
    revenue_by_region = Column(JSONB, nullable=True)
    revenue_by_city = Column(JSONB, nullable=True)
    top_countries = Column(ARRAY(String), nullable=True)
    demographic_breakdown = Column(JSONB, nullable=True)
    
    # Device and platform analytics
    device_breakdown = Column(JSONB, nullable=True)
    browser_breakdown = Column(JSONB, nullable=True)
    app_breakdown = Column(JSONB, nullable=True)
    source_breakdown = Column(JSONB, nullable=True)
    
    # Payment processing
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING_APPROVAL)
    payment_method = Column(String(100), nullable=True)
    payment_processor = Column(String(100), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    payment_batch_id = Column(String(255), nullable=True)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    internal_reference = Column(String(255), nullable=True)
    campaign_id = Column(String(255), nullable=True)
    promotion_code = Column(String(100), nullable=True)
    attribution_data = Column(JSONB, nullable=True)
    
    # Audit and timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="revenue_records")
    content_fingerprint = relationship("ContentFingerprint", back_populates="revenue_records")
    collaboration = relationship("CollaborationRequest", back_populates="revenue_records")
    
    # Indexes for optimization
    __table_args__ = (
        Index('idx_revenue_user_platform', 'user_id', 'platform'),
        Index('idx_revenue_status_date', 'revenue_status', 'transaction_date'),
        Index('idx_revenue_period', 'revenue_period_start', 'revenue_period_end'),
        Index('idx_revenue_amount', 'net_amount'),
        Index('idx_revenue_currency', 'currency'),
        Index('idx_revenue_type_platform', 'revenue_type', 'platform'),
        Index('idx_revenue_payment_status', 'payment_status'),
        Index('idx_revenue_tax_status', 'tax_status'),
        Index('idx_revenue_content', 'content_fingerprint_id'),
        Index('idx_revenue_collaboration', 'collaboration_id'),
        Index('idx_revenue_external_id', 'external_transaction_id'),
        
        # Check constraints for data integrity
        CheckConstraint('gross_amount >= 0', name='check_gross_amount_positive'),
        CheckConstraint('net_amount >= 0', name='check_net_amount_positive'),
        CheckConstraint('platform_fee >= 0', name='check_platform_fee_positive'),
        CheckConstraint('tax_rate_applied >= 0 AND tax_rate_applied <= 100', name='check_tax_rate_valid'),
        CheckConstraint('exchange_rate > 0', name='check_exchange_rate_positive'),
        CheckConstraint('revenue_period_start <= revenue_period_end', name='check_period_valid'),
        
        # Unique constraints
        UniqueConstraint('external_transaction_id', 'platform', name='uq_external_transaction_platform'),
    )
    
    def __repr__(self):
        return f"<RevenueRecord(id={self.id}, user_id={self.user_id}, platform={self.platform.value}, amount={self.net_amount})>"
    
    @property
    def total_deductions(self) -> Decimal:
        """Calculate total deductions from gross amount"""        return (
            self.platform_fee + self.service_fee + self.processing_fee + 
            self.distribution_fee + self.transaction_fee + self.other_deductions +
            self.gross_tax_amount
        )
    
    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage"""        if self.gross_amount == 0:
            return 0.0
        return float((self.net_amount / self.gross_amount) * 100)
    
    @property
    def effective_tax_rate(self) -> float:
        """Calculate effective tax rate"""        if self.gross_amount == 0:
            return 0.0
        return float((self.gross_tax_amount / self.gross_amount) * 100)


class RevenueAggregation(Base):
    """    Revenue Aggregation Model
    
    Pre-calculated aggregations for fast analytics and reporting.
    Optimized for dashboard queries and performance metrics.
    """    __tablename__ = "revenue_aggregations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation scope
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(SQLEnum(PlatformType), nullable=True, index=True)
    revenue_type = Column(SQLEnum(RevenueType), nullable=True, index=True)
    
    # Time dimensions
    aggregation_period = Column(String(20), nullable=False, index=True)  # daily, weekly, monthly, yearly
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Financial aggregations
    total_gross_amount = Column(Numeric(18, 6), default=0.0)
    total_net_amount = Column(Numeric(18, 6), default=0.0)
    total_fees = Column(Numeric(18, 6), default=0.0)
    total_taxes = Column(Numeric(18, 6), default=0.0)
    currency = Column(SQLEnum(Currency), nullable=False)
    
    # Performance aggregations
    total_transactions = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    unique_content_count = Column(Integer, default=0)
    
    # Analytics
    average_revenue_per_transaction = Column(Numeric(18, 6), default=0.0)
    average_revenue_per_play = Column(Numeric(18, 6), default=0.0)
    growth_rate_percent = Column(Numeric(8, 4), default=0.0)
    
    # Metadata
    calculation_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    data_quality_score = Column(Float, default=1.0)
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_agg_user_period', 'user_id', 'aggregation_period', 'period_start'),
        Index('idx_agg_platform_period', 'platform', 'aggregation_period', 'period_start'),
        Index('idx_agg_type_period', 'revenue_type', 'aggregation_period', 'period_start'),
        UniqueConstraint('user_id', 'platform', 'revenue_type', 'aggregation_period', 'period_start', 
                        name='uq_aggregation_scope'),
    )


# Event listeners for automatic calculations
@event.listens_for(RevenueRecord, 'before_insert')
@event.listens_for(RevenueRecord, 'before_update')
def calculate_derived_fields(mapper, connection, target):
    """Automatically calculate derived fields before database operations"""    # Calculate base currency amount if not provided
    if target.base_currency_amount is None and target.exchange_rate:
        target.base_currency_amount = target.net_amount * target.exchange_rate
    
    # Ensure net amount doesn't exceed gross amount
    if target.net_amount > target.gross_amount:
        target.net_amount = target.gross_amount
    
    # Set reporting date if not provided
    if target.reporting_date is None:
        target.reporting_date = datetime.utcnow()


__all__ = [
    'RevenueType',
    'PlatformType', 
    'Currency',
    'RevenueStatus',
    'PaymentStatus',
    'TaxStatus',
    'RevenueRecord',
    'RevenueAggregation'
]
