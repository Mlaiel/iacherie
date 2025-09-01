"""Monetization and Revenue Schemas

Comprehensive Pydantic schemas for revenue tracking, payment processing,
and monetization management in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class CurrencyEnum(str, Enum):
    """
Supported currencies"""

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
    PLN = "PLN"
    BRL = "BRL"
    MXN = "MXN"


class RevenueSourceEnum(str, Enum):
    """Sources of revenue"""

    STREAMING = "streaming"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    SYNC_LICENSING = "sync_licensing"
    MECHANICAL_ROYALTIES = "mechanical_royalties"
    PERFORMANCE_ROYALTIES = "performance_royalties"
    YOUTUBE_MONETIZATION = "youtube_monetization"
    SPOTIFY_STREAMS = "spotify_streams"
    APPLE_MUSIC = "apple_music"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_LICENSING = "content_licensing"
    NFT_SALES = "nft_sales"
    SUBSCRIPTION = "subscription"
    TIPS_DONATIONS = "tips_donations"
    OTHER = "other"


class PaymentStatusEnum(str, Enum):
    """Payment processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"
    REQUIRES_ACTION = "requires_action"


class PaymentMethodEnum(str, Enum):
    """Payment methods"""

    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"
    DIRECT_DEPOSIT = "direct_deposit"
    INTERNATIONAL_WIRE = "international_wire"
    DIGITAL_WALLET = "digital_wallet"


class MonetizationRuleTypeEnum(str, Enum):
    """Types of monetization rules"""

    PERCENTAGE_SPLIT = "percentage_split"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_COMMISSION = "tiered_commission"
    REVENUE_THRESHOLD = "revenue_threshold"
    PLATFORM_SPECIFIC = "platform_specific"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"


class TaxStatusEnum(str, Enum):
    """Tax status categories"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"
    NON_PROFIT = "non_profit"
    INTERNATIONAL = "international"
    TAX_EXEMPT = "tax_exempt"


class RevenueMetricsSchema(BaseModel):
    """Schema for revenue metrics and analytics"""
    total_streams: int = Field(0, description="Total number of streams")
    total_downloads: int = Field(0, description="Total number of downloads")
    total_views: int = Field(0, description="Total number of views")
    unique_listeners: int = Field(0, description="Number of unique listeners")
    engagement_rate: float = Field(0.0, description="Engagement rate percentage")
    conversion_rate: float = Field(0.0, description="Conversion rate percentage")
    average_revenue_per_user: Decimal = Field(Decimal('0.00'), description="ARPU")
    customer_lifetime_value: Decimal = Field(Decimal('0.00'), description="CLV")
    retention_rate: float = Field(0.0, description="User retention rate")
    churn_rate: float = Field(0.0, description="User churn rate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_streams": 100000,
                "total_downloads": 5000,
                "unique_listeners": 15000,
                "engagement_rate": 0.75,
                "average_revenue_per_user": "2.50",
                "retention_rate": 0.85
            }
        }


class PlatformRevenueSchema(BaseModel):
    """Schema for platform-specific revenue data"""
    platform: str = Field(..., description="Platform name")
    revenue_amount: Decimal = Field(..., description="Revenue amount")
    currency: CurrencyEnum = Field(..., description="Currency code")
    streams_count: Optional[int] = Field(None, description="Number of streams")
    downloads_count: Optional[int] = Field(None, description="Number of downloads")
    royalty_rate: Optional[float] = Field(None, description="Royalty rate percentage")
    commission_rate: Optional[float] = Field(None, description="Platform commission rate")
    net_revenue: Decimal = Field(..., description="Net revenue after commissions")
    payout_date: Optional[date] = Field(None, description="Expected payout date")
    payout_status: PaymentStatusEnum = Field(..., description="Payout status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "spotify",
                "revenue_amount": "150.75",
                "currency": "EUR",
                "streams_count": 50000,
                "royalty_rate": 0.004,
                "net_revenue": "135.68",
                "payout_status": "completed"
            }
        }


class RevenueTrackingBaseSchema(BaseModel):
    """Base schema for revenue tracking"""
    user_id: PositiveInt = Field(..., description="User ID")
    content_id: Optional[PositiveInt] = Field(None, description="Associated content ID")
    fingerprint_id: Optional[PositiveInt] = Field(None, description="Associated fingerprint ID")
    
    # Revenue details
    revenue_source: RevenueSourceEnum = Field(..., description="Source of revenue")
    gross_amount: Decimal = Field(..., description="Gross revenue amount")
    currency: CurrencyEnum = Field(..., description="Currency code")
    platform: str = Field(..., description="Platform generating revenue")
    
    # Period information
    period_start: date = Field(..., description="Revenue period start date")
    period_end: date = Field(..., description="Revenue period end date")
    reporting_date: date = Field(..., description="Date revenue was reported")
    
    # Commission and fees
    platform_commission: Decimal = Field(Decimal('0.00'), description="Platform commission amount")
    service_fee: Decimal = Field(Decimal('0.00'), description="Service fee amount")
    processing_fee: Decimal = Field(Decimal('0.00'), description="Payment processing fee")
    tax_amount: Decimal = Field(Decimal('0.00'), description="Tax amount")
    net_amount: Decimal = Field(..., description="Net revenue amount")
    
    # Metrics
    metrics: Optional[RevenueMetricsSchema] = Field(None, description="Associated metrics")
    
    @field_validator('net_amount')
    @classmethod
    def calculate_net_amount(cls, v, values):
        """Calculate net amount from gross minus all fees"""
        gross = values.get('gross_amount', Decimal('0.00'))
        commission = values.get('platform_commission', Decimal('0.00'))
        service_fee = values.get('service_fee', Decimal('0.00'))
        processing_fee = values.get('processing_fee', Decimal('0.00'))
        tax = values.get('tax_amount', Decimal('0.00'))
        
        calculated_net = gross - commission - service_fee - processing_fee - tax
        return calculated_net


class RevenueTrackingCreateSchema(RevenueTrackingBaseSchema):
    """
Schema for creating revenue tracking entries"""
    # Additional metadata
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    reference_id: Optional[str] = Field(None, description="Platform reference ID")
    payment_reference: Optional[str] = Field(None, description="Payment reference")
    
    # Processing options
    auto_payout: bool = Field(True, description="Enable automatic payout")
    hold_payment: bool = Field(False, description="Hold payment for review")
    verify_authenticity: bool = Field(True, description="Verify revenue authenticity")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    notes: Optional[str] = Field(None, description="Revenue notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "content_id": 456,
                "revenue_source": "spotify_streams",
                "gross_amount": "150.00",
                "currency": "EUR",
                "platform": "spotify",
                "period_start": "2024-08-01",
                "period_end": "2024-08-31",
                "platform_commission": "45.00",
                "net_amount": "105.00"
            }
        }


class RevenueTrackingUpdateSchema(BaseModel):
    """Schema for updating revenue tracking entries"""
    gross_amount: Optional[Decimal] = Field(None, description="Updated gross amount")
    platform_commission: Optional[Decimal] = Field(None, description="Updated commission")
    service_fee: Optional[Decimal] = Field(None, description="Updated service fee")
    processing_fee: Optional[Decimal] = Field(None, description="Updated processing fee")
    tax_amount: Optional[Decimal] = Field(None, description="Updated tax amount")
    payment_status: Optional[PaymentStatusEnum] = Field(None, description="Updated payment status")
    notes: Optional[str] = Field(None, description="Updated notes")
    verified: Optional[bool] = Field(None, description="Verification status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "gross_amount": "155.00",
                "platform_commission": "46.50",
                "payment_status": "completed",
                "verified": True
            }
        }


class PaymentProcessingSchema(BaseModel):
    """Schema for payment processing information"""
    payment_id: str = Field(..., description="Unique payment ID")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method used")
    payment_gateway: str = Field(..., description="Payment gateway provider")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    
    # Amount details
    amount: Decimal = Field(..., description="Payment amount")
    currency: CurrencyEnum = Field(..., description="Payment currency")
    exchange_rate: Optional[Decimal] = Field(None, description="Exchange rate if converted")
    
    # Processing details
    processing_started: datetime = Field(..., description="Processing start time")
    processing_completed: Optional[datetime] = Field(None, description="Processing completion time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Status and verification
    status: PaymentStatusEnum = Field(..., description="Payment status")
    verification_required: bool = Field(False, description="Whether verification is required")
    risk_score: Optional[float] = Field(None, description="Risk assessment score")
    
    # Recipient details
    recipient_name: str = Field(..., description="Recipient name")
    recipient_account: str = Field(..., description="Recipient account info")
    recipient_country: str = Field(..., description="Recipient country")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "PAY-2024-001234",
                "payment_method": "bank_transfer",
                "payment_gateway": "stripe",
                "amount": "500.00",
                "currency": "EUR",
                "status": "processing",
                "recipient_name": "John Doe"
            }
        }


class RevenueTrackingResponseSchema(RevenueTrackingBaseSchema):
    """Schema for revenue tracking responses"""
    id: PositiveInt = Field(..., description="Unique revenue tracking ID")
    
    # Status and verification
    status: str = Field(..., description="Revenue tracking status")
    verified: bool = Field(False, description="Whether revenue is verified")
    verification_date: Optional[datetime] = Field(None, description="Verification timestamp")
    
    # Payment information
    payment_status: PaymentStatusEnum = Field(..., description="Payment processing status")
    payment_processing: Optional[PaymentProcessingSchema] = Field(None, description="Payment processing details")
    payout_date: Optional[date] = Field(None, description="Actual payout date")
    
    # Analytics and insights
    revenue_growth: Optional[float] = Field(None, description="Revenue growth percentage")
    market_share: Optional[float] = Field(None, description="Market share percentage")
    competitive_ranking: Optional[int] = Field(None, description="Competitive ranking")
    forecast_next_period: Optional[Decimal] = Field(None, description="Forecasted revenue")
    
    # Platform-specific data
    platform_revenue_breakdown: Optional[List[PlatformRevenueSchema]] = Field(None, description="Revenue by platform")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    audit_trail: Optional[List[Dict]] = Field(None, description="Audit trail")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 123,
                "revenue_source": "spotify_streams",
                "gross_amount": "150.00",
                "net_amount": "105.00",
                "currency": "EUR",
                "status": "verified",
                "payment_status": "completed",
                "revenue_growth": 15.5,
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class MonetizationRuleSchema(BaseModel):
    """Schema for monetization rules and configurations"""
    rule_id: str = Field(..., description="Unique rule identifier")
    user_id: PositiveInt = Field(..., description="User ID")
    rule_name: str = Field(..., description="Rule name")
    rule_type: MonetizationRuleTypeEnum = Field(..., description="Type of monetization rule")
    
    # Rule configuration
    percentage_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage rate")
    fixed_amount: Optional[Decimal] = Field(None, description="Fixed amount")
    minimum_threshold: Optional[Decimal] = Field(None, description="Minimum threshold")
    maximum_cap: Optional[Decimal] = Field(None, description="Maximum cap")
    
    # Conditions
    platforms: Optional[List[str]] = Field(None, description="Applicable platforms")
    content_types: Optional[List[str]] = Field(None, description="Applicable content types")
    revenue_sources: Optional[List[RevenueSourceEnum]] = Field(None, description="Applicable revenue sources")
    date_range: Optional[Dict[str, date]] = Field(None, description="Date range for rule")
    
    # Status
    active: bool = Field(True, description="Whether rule is active")
    priority: int = Field(1, description="Rule priority")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "RULE-2024-001",
                "user_id": 123,
                "rule_name": "Spotify Revenue Split",
                "rule_type": "percentage_split",
                "percentage_rate": 15.0,
                "platforms": ["spotify"],
                "active": True
            }
        }


class RevenueDashboardSchema(BaseModel):
    """Schema for revenue dashboard metrics"""
    # Summary metrics
    total_revenue: Decimal = Field(..., description="Total revenue")
    revenue_this_month: Decimal = Field(..., description="Revenue this month")
    revenue_last_month: Decimal = Field(..., description="Revenue last month")
    revenue_growth: float = Field(..., description="Revenue growth percentage")
    
    # Revenue breakdown
    revenue_by_source: Dict[str, Decimal] = Field(..., description="Revenue by source")
    revenue_by_platform: Dict[str, Decimal] = Field(..., description="Revenue by platform")
    revenue_by_currency: Dict[str, Decimal] = Field(..., description="Revenue by currency")
    
    # Payment status
    pending_payments: Decimal = Field(..., description="Total pending payments")
    completed_payments: Decimal = Field(..., description="Total completed payments")
    failed_payments: Decimal = Field(..., description="Total failed payments")
    
    # Performance metrics
    top_earning_content: List[Dict] = Field(..., description="Top earning content")
    revenue_trends: List[Dict] = Field(..., description="Revenue trends over time")
    payout_schedule: List[Dict] = Field(..., description="Upcoming payouts")
    
    # Analytics
    average_revenue_per_content: Decimal = Field(..., description="Average revenue per content")
    conversion_metrics: Dict[str, float] = Field(..., description="Conversion metrics")
    forecasted_revenue: Dict[str, Decimal] = Field(..., description="Revenue forecasts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_revenue": "15750.50",
                "revenue_this_month": "2250.75",
                "revenue_growth": 18.5,
                "pending_payments": "450.00",
                "average_revenue_per_content": "125.50"
            }
        }


class TaxReportingSchema(BaseModel):
    """Schema for tax reporting information"""
    user_id: PositiveInt = Field(..., description="User ID")
    tax_year: int = Field(..., description="Tax year")
    tax_status: TaxStatusEnum = Field(..., description="Tax status")
    country: str = Field(..., description="Tax country")
    
    # Income summary
    total_income: Decimal = Field(..., description="Total income")
    taxable_income: Decimal = Field(..., description="Taxable income")
    tax_withheld: Decimal = Field(..., description="Tax withheld")
    deductions: Decimal = Field(..., description="Total deductions")
    
    # Breakdown by source
    income_by_source: Dict[str, Decimal] = Field(..., description="Income by source")
    international_income: Decimal = Field(..., description="International income")
    
    # Tax documents
    documents_generated: List[str] = Field(..., description="Generated tax documents")
    filing_deadline: date = Field(..., description="Tax filing deadline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "tax_year": 2024,
                "tax_status": "individual",
                "country": "DE",
                "total_income": "25000.00",
                "taxable_income": "22000.00",
                "documents_generated": ["1099-MISC", "W-8BEN"]
            }
        }


# Export schemas
__all__ = [
    # Enums
    "CurrencyEnum",
    "RevenueSourceEnum",
    "PaymentStatusEnum",
    "PaymentMethodEnum",
    "MonetizationRuleTypeEnum",
    "TaxStatusEnum",
    
    # Complex schemas
    "RevenueMetricsSchema",
    "PlatformRevenueSchema",
    "PaymentProcessingSchema",
    
    # Main schemas
    "RevenueTrackingBaseSchema",
    "RevenueTrackingCreateSchema",
    "RevenueTrackingUpdateSchema",
    "RevenueTrackingResponseSchema",
    
    # Configuration and dashboard
    "MonetizationRuleSchema",
    "RevenueDashboardSchema",
    "TaxReportingSchema"
]
