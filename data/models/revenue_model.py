"""Revenue Data Model
=================

Professional revenue tracking and monetization data model.
Comprehensive revenue analytics with multi-platform support.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


class RevenueSource(Enum):
    """
Revenue source enumeration"""

    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    SUBSCRIPTIONS = "subscriptions"
    TIPS = "tips"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCES = "live_performances"
    COLLABORATION = "collaboration"
    SPONSORSHIP = "sponsorship"
    ROYALTIES = "royalties"
    SYNC_LICENSING = "sync_licensing"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    DIGITAL_SALES = "digital_sales"
    PHYSICAL_SALES = "physical_sales"


class RevenueStatus(Enum):
    """Revenue status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PAID = "paid"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class PaymentMethod(Enum):
    """Payment method enumeration"""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    CHECK = "check"
    CASH = "cash"
    PLATFORM_CREDIT = "platform_credit"


class RevenuePeriod(Enum):
    """Revenue period enumeration"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class RevenueModel(Base):
    """
    Professional revenue data model for IA Influencer Agent platform.
    
    Comprehensive revenue tracking, analytics, and monetization with
    multi-platform support, payment processing, and detailed reporting.
    """
    
    __tablename__ = "revenue"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("content.id"), index=True)
    
    # Revenue basic information
    revenue_source = Column(String(30), nullable=False)  # RevenueSource
    amount = Column(DECIMAL(12, 4), nullable=False)
    currency = Column(String(3), default="EUR")
    amount_usd = Column(DECIMAL(12, 4))  # Converted to USD for analytics
    exchange_rate = Column(DECIMAL(10, 6))  # Exchange rate used
    
    # Period and timing
    revenue_period = Column(String(20), default=RevenuePeriod.MONTHLY.value)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    revenue_date = Column(Date, nullable=False)  # When revenue was earned
    payment_due_date = Column(Date)  # When payment is due
    payment_date = Column(Date)  # When payment was made
    
    # Platform and source details
    platform = Column(String(50))  # YouTube, Spotify, Instagram, etc.
    platform_revenue_id = Column(String(100))  # Platform's revenue ID
    platform_account_id = Column(String(100))  # Platform account identifier
    api_source = Column(String(50))  # API that provided data
    
    # Revenue breakdown
    gross_revenue = Column(DECIMAL(12, 4))  # Before deductions
    platform_fee = Column(DECIMAL(12, 4), default=0)  # Platform commission
    platform_fee_percentage = Column(DECIMAL(5, 2))  # Platform fee %
    service_fee = Column(DECIMAL(12, 4), default=0)  # Our service fee
    service_fee_percentage = Column(DECIMAL(5, 2))  # Our service fee %
    tax_amount = Column(DECIMAL(12, 4), default=0)  # Tax deducted
    tax_percentage = Column(DECIMAL(5, 2))  # Tax rate %
    net_revenue = Column(DECIMAL(12, 4))  # Final amount to creator
    
    # Payment information
    status = Column(String(20), default=RevenueStatus.PENDING.value)
    payment_method = Column(String(30))  # PaymentMethod
    payment_reference = Column(String(100))  # Payment transaction ID
    payment_processor = Column(String(50))  # Stripe, PayPal, etc.
    payment_account = Column(String(100))  # Account used for payment
    
    # Performance metrics
    views_count = Column(Integer, default=0)
    plays_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    streams_count = Column(Integer, default=0)
    impressions_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    engagement_count = Column(Integer, default=0)
    
    # Revenue per metric calculations
    revenue_per_view = Column(DECIMAL(8, 6))  # Revenue per view
    revenue_per_play = Column(DECIMAL(8, 6))  # Revenue per play/stream
    revenue_per_download = Column(DECIMAL(8, 6))  # Revenue per download
    revenue_per_click = Column(DECIMAL(8, 6))  # Revenue per click
    cpm = Column(DECIMAL(8, 4))  # Cost per mille (1000 impressions)
    cpc = Column(DECIMAL(8, 4))  # Cost per click
    ctr = Column(DECIMAL(5, 4))  # Click-through rate
    
    # Geographic and demographic breakdown
    revenue_by_country = Column(JSON)  # Revenue breakdown by country
    revenue_by_age_group = Column(JSON)  # Revenue by audience age
    revenue_by_gender = Column(JSON)  # Revenue by audience gender
    revenue_by_device = Column(JSON)  # Revenue by device type
    revenue_by_source = Column(JSON)  # Revenue by traffic source
    
    # Content-specific metrics
    content_title = Column(String(500))  # Content title at time of revenue
    content_category = Column(String(100))  # Content category
    content_tags = Column(ARRAY(String))  # Content tags
    content_duration = Column(Float)  # Content duration if applicable
    content_quality_score = Column(Float)  # Content quality at time
    
    # Collaboration and sharing
    collaboration_id = Column(String(36))  # If revenue is from collaboration
    revenue_share_config = Column(JSON)  # Revenue sharing configuration
    collaborator_payments = Column(JSON)  # Payments to collaborators
    total_collaborators = Column(Integer, default=0)
    
    # Licensing and rights
    license_type = Column(String(50))  # Type of license generating revenue
    license_duration = Column(Integer)  # License duration in days
    territory = Column(ARRAY(String))  # Geographic territories
    usage_rights = Column(JSON)  # Specific usage rights licensed
    
    # Advertising and sponsorship details
    advertiser_name = Column(String(200))  # Advertiser/sponsor name
    campaign_name = Column(String(200))  # Campaign name
    ad_format = Column(String(50))  # Ad format (banner, video, etc.)
    sponsor_category = Column(String(100))  # Sponsor industry category
    
    # Analytics and insights
    growth_rate = Column(DECIMAL(8, 4))  # Revenue growth rate %
    seasonal_factor = Column(DECIMAL(6, 4))  # Seasonal adjustment factor
    predicted_revenue = Column(DECIMAL(12, 4))  # AI predicted revenue
    confidence_level = Column(DECIMAL(5, 2))  # Prediction confidence %
    
    # Quality and verification
    data_quality_score = Column(Float, default=100.0)  # Data quality rating
    verified = Column(Boolean, default=False)  # Manual verification
    verified_by = Column(String(36))  # User ID who verified
    verified_at = Column(DateTime)  # Verification timestamp
    audit_trail = Column(JSON)  # Audit log for changes
    
    # Metadata and tags
    meta_data = Column(JSON)  # Flexible metadata storage
    tags = Column(ARRAY(String))  # Revenue tags
    notes = Column(Text)  # Additional notes
    categories = Column(ARRAY(String))  # Revenue categories
    
    # Fraud detection and security
    fraud_score = Column(Float, default=0.0)  # 0-100 fraud probability
    anomaly_detected = Column(Boolean, default=False)
    risk_level = Column(String(20), default="low")  # low, medium, high
    security_flags = Column(JSON)  # Security-related flags
    
    # Recurring revenue
    is_recurring = Column(Boolean, default=False)
    recurrence_frequency = Column(String(20))  # daily, weekly, monthly, etc.
    next_expected_date = Column(Date)  # Next expected revenue date
    recurring_amount = Column(DECIMAL(12, 4))  # Expected recurring amount
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)  # When revenue was processed
    reconciled_at = Column(DateTime)  # When revenue was reconciled
    
    # Soft delete
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="revenue_records")
    content = relationship("ContentModel", back_populates="revenue_records")
    
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
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'revenue_source': self.revenue_source,
            'amount': float(self.amount) if self.amount else 0.0,
            'currency': self.currency,
            'amount_usd': float(self.amount_usd) if self.amount_usd else None,
            'revenue_period': self.revenue_period,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'revenue_date': self.revenue_date.isoformat() if self.revenue_date else None,
            'platform': self.platform,
            'gross_revenue': float(self.gross_revenue) if self.gross_revenue else None,
            'platform_fee': float(self.platform_fee) if self.platform_fee else 0.0,
            'service_fee': float(self.service_fee) if self.service_fee else 0.0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0.0,
            'net_revenue': float(self.net_revenue) if self.net_revenue else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'views_count': self.views_count,
            'plays_count': self.plays_count,
            'streams_count': self.streams_count,
            'revenue_per_view': float(self.revenue_per_view) if self.revenue_per_view else None,
            'revenue_per_play': float(self.revenue_per_play) if self.revenue_per_play else None,
            'cpm': float(self.cpm) if self.cpm else None,
            'content_title': self.content_title,
            'content_category': self.content_category,
            'growth_rate': float(self.growth_rate) if self.growth_rate else None,
            'verified': self.verified,
            'is_recurring': self.is_recurring,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
    
    @property
    def is_paid(self) -> bool:
        """
Check if revenue has been paid"""
        return self.status == RevenueStatus.PAID.value
    
    @property
    def is_pending(self) -> bool:
        """
Check if revenue is pending"""
        return self.status == RevenueStatus.PENDING.value
    
    @property
    def is_streaming_revenue(self) -> bool:
        """
Check if revenue is from streaming"""
        return self.revenue_source == RevenueSource.STREAMING.value
    
    @property
    def is_advertising_revenue(self) -> bool:
        """
Check if revenue is from advertising"""
        return self.revenue_source == RevenueSource.ADVERTISING.value
    
    @property
    def amount_formatted(self) -> str:
        """
Get formatted amount with currency"""
        if self.amount:
            return f"{self.currency} {self.amount:,.2f}"
        return f"{self.currency} 0.00"
    
    @property
    def net_margin_percentage(self) -> float:
        """Calculate net margin percentage"""
        if self.gross_revenue and self.gross_revenue > 0:
            return float((self.net_revenue / self.gross_revenue) * 100)
        return 0.0
    
    @property
    def total_fees(self) -> Decimal:
        """
Calculate total fees"""
        fees = Decimal('0')
        if self.platform_fee:
            fees += self.platform_fee
        if self.service_fee:
            fees += self.service_fee
        if self.tax_amount:
            fees += self.tax_amount
        return fees
    
    @property
    def period_duration_days(self) -> int:
        """
Calculate period duration in days"""
        if self.period_start and self.period_end:
            return (self.period_end - self.period_start).days + 1
        return 0
    
    @property
    def revenue_per_day(self) -> Optional[Decimal]:
        """
Calculate average revenue per day in period"""
        duration = self.period_duration_days
        if duration > 0 and self.amount:
            return self.amount / duration
        return None
    
    @property
    def is_overdue(self) -> bool:
        """
Check if payment is overdue"""
        if self.payment_due_date and self.status != RevenueStatus.PAID.value:
            return date.today() > self.payment_due_date
        return False
    
    @property
    def performance_rating(self) -> str:
        """
Get performance rating based on metrics"""
        if not self.revenue_per_view:
            return "No Data"
        
        # These thresholds would be industry-specific
        rpm = float(self.revenue_per_view * 1000)  # Revenue per mille
        
        if rpm >= 5.0:
            return "Excellent"
        elif rpm >= 2.0:
            return "Good"
        elif rpm >= 1.0:
            return "Average"
        elif rpm >= 0.5:
            return "Below Average"
        else:
            return "Poor"
    
    def calculate_net_revenue(self):
        """Calculate net revenue after all deductions"""
        if not self.gross_revenue:
            self.net_revenue = self.amount
            return
        
        net = self.gross_revenue
        
        if self.platform_fee:
            net -= self.platform_fee
        if self.service_fee:
            net -= self.service_fee
        if self.tax_amount:
            net -= self.tax_amount
        
        self.net_revenue = max(Decimal('0'), net)
        self.updated_at = datetime.utcnow()
    
    def calculate_fees_from_percentage(self):
        """
Calculate fee amounts from percentages"""
        if not self.gross_revenue:
            return
        
        if self.platform_fee_percentage:
            self.platform_fee = (self.gross_revenue * self.platform_fee_percentage) / 100
        
        if self.service_fee_percentage:
            self.service_fee = (self.gross_revenue * self.service_fee_percentage) / 100
        
        if self.tax_percentage:
            self.tax_amount = (self.gross_revenue * self.tax_percentage) / 100
        
        self.calculate_net_revenue()
    
    def calculate_performance_metrics(self):
        """
Calculate performance metrics"""
        if self.amount and self.amount > 0:
            # Revenue per metric calculations
            if self.views_count and self.views_count > 0:
                self.revenue_per_view = self.amount / self.views_count
            
            if self.plays_count and self.plays_count > 0:
                self.revenue_per_play = self.amount / self.plays_count
            
            if self.downloads_count and self.downloads_count > 0:
                self.revenue_per_download = self.amount / self.downloads_count
            
            if self.clicks_count and self.clicks_count > 0:
                self.revenue_per_click = self.amount / self.clicks_count
            
            # CPM calculation
            if self.impressions_count and self.impressions_count > 0:
                self.cpm = (self.amount / self.impressions_count) * 1000
            
            # CPC calculation
            if self.clicks_count and self.clicks_count > 0:
                self.cpc = self.amount / self.clicks_count
            
            # CTR calculation
            if self.impressions_count and self.clicks_count and self.impressions_count > 0:
                self.ctr = (self.clicks_count / self.impressions_count) * 100
        
        self.updated_at = datetime.utcnow()
    
    def convert_to_usd(self, exchange_rate: Decimal):
        """
Convert amount to USD"""
        if self.amount and exchange_rate:
            self.amount_usd = self.amount * exchange_rate
            self.exchange_rate = exchange_rate
            self.updated_at = datetime.utcnow()
    
    def mark_as_paid(self, payment_reference: str = None, payment_method: str = None):
        """
Mark revenue as paid"""
        self.status = RevenueStatus.PAID.value
        self.payment_date = date.today()
        self.processed_at = datetime.utcnow()
        
        if payment_reference:
            self.payment_reference = payment_reference
        if payment_method:
            self.payment_method = payment_method
        
        self.updated_at = datetime.utcnow()
    
    def dispute_revenue(self, reason: str = None):
        """
Mark revenue as disputed"""
        self.status = RevenueStatus.DISPUTED.value
        
        if reason:
        try:
            logger.info(f"Executing refund_revenue")
            
            # Implementation for refund_revenue
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"refund_revenue completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"refund_revenue failed: {e}")
            raise
        if refund_amount:
            # Create negative revenue record for refund
            pass  # Implementation would create refund record
        
        if reason:
            if not self.notes:
                self.notes = f"Refunded: {reason}"
            else:
                self.notes += f"\nRefunded: {reason}"
        
        self.updated_at = datetime.utcnow()
    
    def verify_revenue(self, verified_by: str):
        """Mark revenue as verified"""
        self.verified = True
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def flag_anomaly(self, reason: str = None, risk_level: str = "medium"):
        """Flag revenue as anomalous"""
        self.anomaly_detected = True
        self.risk_level = risk_level
        
        if reason:
            security_flags = self.security_flags or {}
            security_flags['anomaly_reason'] = reason
            security_flags['flagged_at'] = datetime.utcnow().isoformat()
            self.security_flags = security_flags
        
        self.updated_at = datetime.utcnow()
    
    def set_recurring(self, frequency: str, next_date: date, amount: Decimal = None):
        """
Set revenue as recurring"""
        self.is_recurring = True
        self.recurrence_frequency = frequency
        self.next_expected_date = next_date
        self.recurring_amount = amount or self.amount
        self.updated_at = datetime.utcnow()
    
    def add_collaborator_payment(self, collaborator_id: str, amount: Decimal, percentage: float):
        """
Add collaborator payment information"""
        if not self.collaborator_payments:
            self.collaborator_payments = {}
        
        self.collaborator_payments[collaborator_id] = {
            'amount': float(amount),
            'percentage': percentage,
            'currency': self.currency,
            'paid_at': None
        }
        
        self.total_collaborators = len(self.collaborator_payments)
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """
Soft delete revenue record"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """
Restore soft-deleted revenue record"""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
