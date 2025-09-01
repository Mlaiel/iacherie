"""Monetization Database Configuration Module for IA-Influencer Agent Platform
===========================================================================

Professional monetization database configuration for revenue tracking, 
payment processing, platform analytics, and automated distribution systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import asyncpg
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

logger = logging.getLogger(__name__)

Base = declarative_base()


class Platform(Enum):
    """Supported monetization platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    ONLYFANS = "onlyfans"
    PATREON = "patreon"
    CUSTOM = "custom"


class RevenueType(Enum):
    """Revenue stream types"""
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    TIPS = "tips"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    DIRECT_SALES = "direct_sales"
    ROYALTIES = "royalties"
    BRAND_DEALS = "brand_deals"
    LIVE_STREAMING = "live_streaming"
    CONTENT_SALES = "content_sales"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


class DistributionStatus(Enum):
    """Revenue distribution status"""
    CALCULATED = "calculated"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class MonetizationCredentials:
    """Monetization database authentication and API credentials"""
    database_url: str = os.getenv("MONETIZATION_DATABASE_URL", "postgresql://user:pass@localhost:5432/monetization")
    redis_url: str = os.getenv("MONETIZATION_REDIS_URL", "redis://localhost:6379/3")
    
    # Payment processor credentials
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    wise_api_key: str = os.getenv("WISE_API_KEY", "")
    
    # Platform API credentials
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    spotify_client_id: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    spotify_client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    pool_size: int = 25
    max_overflow: int = 50


@dataclass
class RevenueTrackingConfig:
    """Revenue tracking configuration"""
    auto_sync_enabled: bool = True
    sync_interval_hours: int = 6
    historical_data_days: int = 365
    minimum_payout_threshold: Decimal = Decimal("50.00")
    currency_conversion_enabled: bool = True
    tax_calculation_enabled: bool = True
    commission_rate: Decimal = Decimal("0.05")  # 5% platform commission
    
    # Platform-specific settings
    platform_configs: Dict[Platform, Dict[str, Any]] = field(default_factory=dict)
    
    # Data accuracy settings
    data_validation_enabled: bool = True
    anomaly_detection: bool = True
    fraud_detection: bool = True
    reconciliation_frequency: int = 24  # hours


@dataclass
class PaymentProcessingConfig:
    """Payment processing configuration"""
    primary_processor: str = "stripe"
    fallback_processors: List[str] = field(default_factory=lambda: ["paypal", "wise"])
    
    auto_payout_enabled: bool = False
    payout_schedule: str = "monthly"  # daily, weekly, monthly
    payout_threshold: Decimal = Decimal("100.00")
    
    # Security settings
    transaction_limits: Dict[str, Decimal] = field(default_factory=lambda: {
        "daily": Decimal("10000.00"),
        "monthly": Decimal("100000.00")
    })
    
    fraud_protection: bool = True
    kyc_required: bool = True
    aml_compliance: bool = True
    
    # Fee structure
    processing_fees: Dict[str, Decimal] = field(default_factory=lambda: {
        "stripe": Decimal("0.029"),  # 2.9%
        "paypal": Decimal("0.034"),  # 3.4%
        "wise": Decimal("0.015")     # 1.5%
    })


@dataclass
class AnalyticsConfig:
    """Revenue analytics configuration"""
    real_time_analytics: bool = True
    predictive_analytics: bool = True
    trend_analysis: bool = True
    comparative_analysis: bool = True
    
    # Reporting settings
    automated_reports: bool = True
    report_frequency: str = "weekly"
    dashboard_refresh_interval: int = 300  # seconds
    
    # Data retention
    raw_data_retention_days: int = 730  # 2 years
    aggregated_data_retention_years: int = 7
    
    # Performance metrics
    calculate_roi: bool = True
    track_conversion_rates: bool = True
    audience_analytics: bool = True
    content_performance_correlation: bool = True


class RevenueTracking(Base):
    """Revenue tracking table"""
    __tablename__ = 'revenue_tracking'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content_id = Column(Integer, nullable=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    revenue_type = Column(String(50), nullable=False)
    
    # Financial data
    gross_revenue = Column(Numeric(12, 4), nullable=False)
    platform_fee = Column(Numeric(12, 4), default=0)
    our_commission = Column(Numeric(12, 4), default=0)
    net_revenue = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), default=Currency.EUR.value)
    
    # Performance metrics
    views = Column(Integer, default=0)
    engagements = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    cpm = Column(Numeric(8, 4), default=0)  # Cost per mille
    cpc = Column(Numeric(8, 4), default=0)  # Cost per click
    
    # Temporal data
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    platform_reference_id = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)


class PaymentTransaction(Base):
    """Payment transactions table"""
    __tablename__ = 'payment_transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    transaction_id = Column(String(255), unique=True, nullable=False)
    
    # Payment details
    amount = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    processor = Column(String(50), nullable=False)
    processor_transaction_id = Column(String(255), nullable=True)
    
    # Status and metadata
    status = Column(String(20), default=PaymentStatus.PENDING.value, index=True)
    payment_method = Column(String(50), nullable=True)
    recipient_info = Column(JSON, nullable=True)
    processor_response = Column(JSON, nullable=True)
    
    # Fees and calculations
    processing_fee = Column(Numeric(10, 4), default=0)
    platform_fee = Column(Numeric(10, 4), default=0)
    net_amount = Column(Numeric(12, 4), nullable=False)
    
    # Temporal tracking
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data
    failure_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)


class RevenueDistribution(Base):
    """Revenue distribution tracking"""
    __tablename__ = 'revenue_distributions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Distribution calculations
    total_gross_revenue = Column(Numeric(12, 4), nullable=False)
    total_platform_fees = Column(Numeric(12, 4), default=0)
    total_our_commission = Column(Numeric(12, 4), default=0)
    total_processing_fees = Column(Numeric(12, 4), default=0)
    distributable_amount = Column(Numeric(12, 4), nullable=False)
    
    # Status tracking
    status = Column(String(20), default=DistributionStatus.CALCULATED.value)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    distributed_at = Column(DateTime, nullable=True)
    
    # Payment details
    payment_transaction_id = Column(String(255), nullable=True)
    payment_method = Column(String(50), nullable=True)
    currency = Column(String(3), default=Currency.EUR.value)
    
    # Metadata
    breakdown_data = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlatformIntegration(Base):
    """Platform integration status"""
    __tablename__ = 'platform_integrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    
    # Integration status
    is_connected = Column(Boolean, default=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Platform-specific data
    platform_user_id = Column(String(255), nullable=True)
    platform_username = Column(String(255), nullable=True)
    channel_id = Column(String(255), nullable=True)
    
    # Sync settings
    auto_sync_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    sync_errors = Column(JSON, nullable=True)
    
    # Metadata
    integration_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class MonetizationConfig:
    """Professional monetization configuration"""
    
    # Database and API credentials
    credentials: MonetizationCredentials = field(default_factory=MonetizationCredentials)
    
    # Revenue tracking configuration
    revenue_tracking: RevenueTrackingConfig = field(default_factory=RevenueTrackingConfig)
    
    # Payment processing configuration
    payment_processing: PaymentProcessingConfig = field(default_factory=PaymentProcessingConfig)
    
    # Analytics configuration
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    
    # Performance settings
    max_concurrent_syncs: int = 50
    batch_size: int = 500
    cache_ttl: int = 1800  # 30 minutes
    rate_limit_per_minute: int = 100
    
    # Feature flags
    real_time_revenue_tracking: bool = True
    automated_payouts: bool = False
    multi_currency_support: bool = True
    tax_reporting: bool = True
    fraud_detection: bool = True
    
    # Notification settings
    email_notifications: bool = True
    webhook_notifications: bool = True
    dashboard_alerts: bool = True
    
    def __post_init__(self):
        """Initialize platform-specific configurations"""
        if not self.revenue_tracking.platform_configs:
            self.revenue_tracking.platform_configs = {
                Platform.YOUTUBE: {
                    "sync_interval": 6,
                    "data_retention_days": 730,
                    "auto_verify": True
                },
                Platform.INSTAGRAM: {
                    "sync_interval": 12,
                    "data_retention_days": 365,
                    "auto_verify": False
                },
                Platform.SPOTIFY: {
                    "sync_interval": 24,
                    "data_retention_days": 1095,
                    "auto_verify": True
                }
            }


class MonetizationManager:
    """Professional monetization database manager"""
    
    def __init__(self, config: MonetizationConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
        self._redis_pool = None
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize monetization database connections"""
        try:
            # Initialize PostgreSQL connection
            self._engine = create_engine(
                self.config.credentials.database_url,
                pool_size=self.config.credentials.pool_size,
                max_overflow=self.config.credentials.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Initialize Redis connection for caching
            self._redis_pool = redis.from_url(
                self.config.credentials.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=25
            )
            
            # Create tables if they don't exist
            Base.metadata.create_all(self._engine)
            
            # Test connections
            await self._test_connections()
            
            self._is_initialized = True
            logger.info("Monetization database manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize monetization manager: {e}")
            return False
    
    async def _test_connections(self):
        """Test database connections"""
        # Test PostgreSQL
        with self._engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Test Redis
        await self._redis_pool.ping()
    
    async def track_revenue(self,
                          user_id: int,
                          platform: Platform,
                          revenue_type: RevenueType,
                          gross_revenue: Decimal,
                          currency: Currency = Currency.EUR,
                          period_start: datetime = None,
                          period_end: datetime = None,
                          metadata: Optional[Dict] = None) -> int:
        """Track revenue from platform"""
        try:
            if period_start is None:
                period_start = datetime.utcnow() - timedelta(days=1)
            if period_end is None:
                period_end = datetime.utcnow()
            
            # Calculate fees
            platform_fee = gross_revenue * Decimal("0.30")  # Typical platform fee
            our_commission = gross_revenue * self.config.revenue_tracking.commission_rate
            net_revenue = gross_revenue - platform_fee - our_commission
            
            with self._session_factory() as session:
                revenue_record = RevenueTracking(
                    user_id=user_id,
                    platform=platform.value,
                    revenue_type=revenue_type.value,
                    gross_revenue=gross_revenue,
                    platform_fee=platform_fee,
                    our_commission=our_commission,
                    net_revenue=net_revenue,
                    currency=currency.value,
                    period_start=period_start,
                    period_end=period_end,
                    metadata=metadata
                )
                
                session.add(revenue_record)
                session.commit()
                session.refresh(revenue_record)
                
                # Cache for quick access
                await self._redis_pool.setex(
                    f"revenue:{user_id}:{platform.value}:{revenue_record.id}",
                    self.config.cache_ttl,
                    str(float(gross_revenue))
                )
                
                logger.info(f"Tracked revenue {revenue_record.id} for user {user_id}: {gross_revenue} {currency.value}")
                return revenue_record.id
                
        except Exception as e:
            logger.error(f"Failed to track revenue: {e}")
            raise
    
    async def process_payment(self,
                            user_id: int,
                            amount: Decimal,
                            currency: Currency = Currency.EUR,
                            processor: str = "stripe",
                            recipient_info: Optional[Dict] = None) -> str:
        """Process payment to creator"""
        try:
            transaction_id = f"txn_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}"
            
            # Calculate fees
            processing_fee = amount * self.config.payment_processing.processing_fees.get(processor, Decimal("0.03"))
            platform_fee = amount * Decimal("0.05")  # 5% platform fee
            net_amount = amount - processing_fee - platform_fee
            
            with self._session_factory() as session:
                transaction = PaymentTransaction(
                    user_id=user_id,
                    transaction_id=transaction_id,
                    amount=amount,
                    currency=currency.value,
                    processor=processor,
                    processing_fee=processing_fee,
                    platform_fee=platform_fee,
                    net_amount=net_amount,
                    recipient_info=recipient_info,
                    status=PaymentStatus.PENDING.value
                )
                
                session.add(transaction)
                session.commit()
                session.refresh(transaction)
                
                logger.info(f"Payment transaction {transaction_id} created for user {user_id}")
                return transaction_id
                
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            raise
    
    async def calculate_distribution(self,
                                   user_id: int,
                                   period_start: datetime,
                                   period_end: datetime) -> int:
        """Calculate revenue distribution for period"""
        try:
            with self._session_factory() as session:
                # Get all revenue for the period
                revenues = session.query(RevenueTracking).filter(
                    RevenueTracking.user_id == user_id,
                    RevenueTracking.period_start >= period_start,
                    RevenueTracking.period_end <= period_end
                ).all()
                
                if not revenues:
                    return 0
                
                # Calculate totals
                total_gross = sum(r.gross_revenue for r in revenues)
                total_platform_fees = sum(r.platform_fee for r in revenues)
                total_commission = sum(r.our_commission for r in revenues)
                total_processing_fees = Decimal("0")  # Will be calculated during payout
                
                distributable = total_gross - total_platform_fees - total_commission
                
                distribution = RevenueDistribution(
                    user_id=user_id,
                    period_start=period_start,
                    period_end=period_end,
                    total_gross_revenue=total_gross,
                    total_platform_fees=total_platform_fees,
                    total_our_commission=total_commission,
                    total_processing_fees=total_processing_fees,
                    distributable_amount=distributable,
                    status=DistributionStatus.CALCULATED.value
                )
                
                session.add(distribution)
                session.commit()
                session.refresh(distribution)
                
                logger.info(f"Distribution {distribution.id} calculated for user {user_id}: {distributable}")
                return distribution.id
                
        except Exception as e:
            logger.error(f"Failed to calculate distribution: {e}")
            raise
    
    async def get_revenue_analytics(self, 
                                  user_id: int,
                                  days_back: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            with self._session_factory() as session:
                revenues = session.query(RevenueTracking).filter(
                    RevenueTracking.user_id == user_id,
                    RevenueTracking.created_at >= cutoff_date
                ).all()
                
                if not revenues:
                    return {"message": "No revenue data found"}
                
                analytics = {
                    "total_revenue": sum(float(r.gross_revenue) for r in revenues),
                    "net_revenue": sum(float(r.net_revenue) for r in revenues),
                    "total_transactions": len(revenues),
                    "average_per_transaction": 0,
                    "revenue_by_platform": {},
                    "revenue_by_type": {},
                    "trend_data": []
                }
                
                if revenues:
                    analytics["average_per_transaction"] = analytics["total_revenue"] / len(revenues)
                
                # Group by platform
                for revenue in revenues:
                    platform = revenue.platform
                    if platform not in analytics["revenue_by_platform"]:
                        analytics["revenue_by_platform"][platform] = 0
                    analytics["revenue_by_platform"][platform] += float(revenue.gross_revenue)
                
                # Group by type
                for revenue in revenues:
                    rev_type = revenue.revenue_type
                    if rev_type not in analytics["revenue_by_type"]:
                        analytics["revenue_by_type"][rev_type] = 0
                    analytics["revenue_by_type"][rev_type] += float(revenue.gross_revenue)
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {e}")
            return {"error": str(e)}
    
    async def sync_platform_data(self, user_id: int, platform: Platform) -> bool:
        """Sync revenue data from platform"""
        try:
            # This would integrate with platform APIs
            logger.info(f"Syncing {platform.value} data for user {user_id}")
            
            # Update last sync time
            with self._session_factory() as session:
                integration = session.query(PlatformIntegration).filter_by(
                    user_id=user_id,
                    platform=platform.value
                ).first()
                
                if integration:
                    integration.last_sync_at = datetime.utcnow()
                    integration.next_sync_at = datetime.utcnow() + timedelta(
                        hours=self.config.revenue_tracking.sync_interval_hours
                    )
                    session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync platform data: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown monetization manager"""
        try:
            if self._redis_pool:
                await self._redis_pool.close()
            
            if self._engine:
                self._engine.dispose()
            
            self._is_initialized = False
            logger.info("Monetization manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during monetization manager shutdown: {e}")


def create_monetization_config() -> MonetizationConfig:
    """Create default monetization configuration"""
    return MonetizationConfig()


def create_monetization_manager(config: Optional[MonetizationConfig] = None) -> MonetizationManager:
    """Create monetization manager with configuration"""
    if config is None:
        config = create_monetization_config()
    return MonetizationManager(config)


# Export configuration for production use
__all__ = [
    'Platform',
    'RevenueType',
    'PaymentStatus',
    'Currency',
    'DistributionStatus',
    'MonetizationConfig',
    'MonetizationManager',
    'RevenueTrackingConfig',
    'PaymentProcessingConfig',
    'AnalyticsConfig',
    'create_monetization_config',
    'create_monetization_manager'
]
