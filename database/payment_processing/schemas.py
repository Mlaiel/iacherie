"""Payment Processing Database Schemas

Advanced Pydantic schemas for payment processing data validation,
serialization, and API documentation.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Payment Systems Specialist + API Architect
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from datetime import datetime
from enum import Enum
import uuid
import re

# Import enum classes from models
from .models import PaymentStatus, PaymentMethodType, BillingFrequency, CurrencyCode


class PaymentStatusEnum(str, Enum):
    """
Payment status enumeration for API"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"


class PaymentMethodTypeEnum(str, Enum):
    """Payment method type enumeration for API"""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class CurrencyEnum(str, Enum):
    """Currency enumeration for API"""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    BTC = "BTC"
    ETH = "ETH"


# Base schemas
class BasePaymentSchema(BaseModel):
    """Base schema for payment-related models"""
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            uuid.UUID: lambda v: str(v)
        }


class AddressSchema(BasePaymentSchema):
    """
Address schema for billing and shipping"""
    line1: str = Field(..., min_length=1, max_length=255)
    line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    
    @validator('country')
    def validate_country_code(cls, v):
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('Country must be a valid ISO 3166-1 alpha-2 code')
        return v


# Payment Transaction Schemas
class PaymentTransactionCreateSchema(BasePaymentSchema):
    """Schema for creating payment transactions"""
    user_id: int = Field(..., gt=0)
    payment_method_id: Optional[uuid.UUID] = None
    transaction_type: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: CurrencyEnum = CurrencyEnum.EUR
    processor: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None
    content_id: Optional[int] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class PaymentTransactionUpdateSchema(BasePaymentSchema):
    """
Schema for updating payment transactions"""
    status: Optional[PaymentStatusEnum] = None
    external_transaction_id: Optional[str] = Field(None, max_length=255)
    processor_response: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None


class PaymentTransactionResponseSchema(BasePaymentSchema):
    """
Schema for payment transaction responses"""
    id: uuid.UUID
    user_id: int
    payment_method_id: Optional[uuid.UUID]
    transaction_type: str
    amount: Decimal
    currency: str
    status: str
    gross_amount: Decimal
    fees_amount: Decimal
    net_amount: Decimal
    processor: str
    external_transaction_id: Optional[str]
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    processed_at: Optional[datetime]
    settled_at: Optional[datetime]


# Payment Method Schemas
class PaymentMethodCreateSchema(BasePaymentSchema):
    """
Schema for creating payment methods"""
    user_id: int = Field(..., gt=0)
    method_type: PaymentMethodTypeEnum
    provider: str = Field(..., min_length=1, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    nickname: Optional[str] = Field(None, max_length=100)
    billing_address: Optional[AddressSchema] = None
    is_default: bool = False
    
    # Card-specific fields
    last_four_digits: Optional[str] = Field(None, regex=r'^\d{4}$')
    brand: Optional[str] = Field(None, max_length=50)
    exp_month: Optional[int] = Field(None, ge=1, le=12)
    exp_year: Optional[int] = Field(None, ge=2024, le=2050)
    
    # Bank account fields
    bank_name: Optional[str] = Field(None, max_length=255)
    account_type: Optional[str] = Field(None, max_length=50)
    routing_number_last_four: Optional[str] = Field(None, regex=r'^\d{4}$')
    
    @root_validator
    def validate_card_fields(cls, values):
        method_type = values.get('method_type')
        if method_type in [PaymentMethodTypeEnum.CREDIT_CARD, PaymentMethodTypeEnum.DEBIT_CARD]:
            required_fields = ['last_four_digits', 'brand', 'exp_month', 'exp_year']
            for field in required_fields:
                if not values.get(field):
                    raise ValueError(f'{field} is required for card payment methods')
        return values


class PaymentMethodResponseSchema(BasePaymentSchema):
    """
Schema for payment method responses"""
    id: uuid.UUID
    user_id: int
    method_type: str
    provider: str
    last_four_digits: Optional[str]
    brand: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    bank_name: Optional[str]
    account_type: Optional[str]
    is_active: bool
    is_verified: bool
    is_default: bool
    nickname: Optional[str]
    created_at: datetime
    verified_at: Optional[datetime]
    last_used_at: Optional[datetime]


# Billing Record Schemas
class BillingRecordCreateSchema(BasePaymentSchema):
    """
Schema for creating billing records"""
    user_id: int = Field(..., gt=0)
    subscription_type: str = Field(..., min_length=1, max_length=100)
    billing_frequency: BillingFrequency
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: CurrencyEnum = CurrencyEnum.EUR
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: Optional[datetime] = None
    usage_metrics: Optional[Dict[str, Any]] = None
    
    @validator('billing_period_end')
    def validate_billing_period(cls, v, values):
        start_date = values.get('billing_period_start')
        if start_date and v <= start_date:
            raise ValueError('Billing period end must be after start date')
        return v


class BillingRecordResponseSchema(BasePaymentSchema):
    """
Schema for billing record responses"""
    id: uuid.UUID
    user_id: int
    subscription_type: str
    billing_frequency: str
    amount: Decimal
    currency: str
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: datetime
    status: str
    is_prorated: bool
    invoice_number: Optional[str]
    usage_metrics: Optional[Dict[str, Any]]
    created_at: datetime
    billed_at: Optional[datetime]
    paid_at: Optional[datetime]


# Financial Record Schemas
class FinancialRecordCreateSchema(BasePaymentSchema):
    """
Schema for creating financial records"""
    user_id: int = Field(..., gt=0)
    record_type: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    amount: Decimal = Field(..., decimal_places=2)
    currency: CurrencyEnum = CurrencyEnum.EUR
    transaction_date: datetime
    source_platform: Optional[str] = Field(None, max_length=100)
    content_id: Optional[int] = None
    revenue_source: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        # Allow negative amounts for expenses/refunds
        return v


class FinancialRecordResponseSchema(BasePaymentSchema):
    """
Schema for financial record responses"""
    id: uuid.UUID
    user_id: int
    record_type: str
    category: str
    subcategory: Optional[str]
    amount: Decimal
    currency: str
    exchange_rate: Optional[Decimal]
    base_currency_amount: Optional[Decimal]
    source_platform: Optional[str]
    content_id: Optional[int]
    revenue_source: Optional[str]
    tax_amount: Decimal
    is_tax_deductible: bool
    transaction_date: datetime
    accounting_period: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime


# Automated Payout Schemas
class AutomatedPayoutCreateSchema(BasePaymentSchema):
    """
Schema for creating automated payouts"""
    user_id: int = Field(..., gt=0)
    payment_method_id: uuid.UUID
    payout_frequency: str = Field(..., min_length=1, max_length=20)
    minimum_amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: CurrencyEnum = CurrencyEnum.EUR
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    period_start: datetime
    period_end: datetime
    processor: str = Field(..., min_length=1, max_length=50)
    revenue_breakdown: Optional[Dict[str, Any]] = None
    
    @validator('period_end')
    def validate_period(cls, v, values):
        start_date = values.get('period_start')
        if start_date and v <= start_date:
            raise ValueError('Period end must be after start date')
        return v
    
    @validator('total_amount')
    def validate_minimum_amount(cls, v, values):
        minimum = values.get('minimum_amount')
        if minimum and v < minimum:
            raise ValueError('Total amount must be at least the minimum amount')
        return v


class AutomatedPayoutResponseSchema(BasePaymentSchema):
    """
Schema for automated payout responses"""
    id: uuid.UUID
    user_id: int
    payment_method_id: uuid.UUID
    payout_frequency: str
    minimum_amount: Decimal
    currency: str
    total_amount: Decimal
    fees_amount: Decimal
    net_amount: Decimal
    period_start: datetime
    period_end: datetime
    status: str
    processor: str
    external_payout_id: Optional[str]
    revenue_breakdown: Optional[Dict[str, Any]]
    content_items_count: int
    platforms_count: int
    is_approved: bool
    scheduled_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int
    last_error: Optional[str]
    created_at: datetime


# Analytics and Reporting Schemas
class RevenueAnalyticsSchema(BasePaymentSchema):
    """
Schema for revenue analytics"""
    total_revenue: Decimal
    transaction_count: int
    average_transaction: Decimal
    period_start: datetime
    period_end: datetime
    currency: str


class RevenueTrendSchema(BasePaymentSchema):
    """
Schema for revenue trend data"""
    date: str
    revenue: Decimal
    transactions: int


class PlatformRevenueSchema(BasePaymentSchema):
    """
Schema for platform revenue breakdown"""
    platform: str
    revenue: Decimal
    transactions: int
    percentage: Optional[float] = None


class FinancialSummarySchema(BasePaymentSchema):
    """
Schema for financial summary"""
    period: str
    total_amount: Decimal
    record_count: int
    categories: List[Dict[str, Any]]


# Query and Filter Schemas
class PaymentTransactionFilterSchema(BasePaymentSchema):
    """
Schema for filtering payment transactions"""
    user_id: Optional[int] = None
    status: Optional[PaymentStatusEnum] = None
    transaction_type: Optional[str] = None
    currency: Optional[CurrencyEnum] = None
    processor: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class PaymentMethodFilterSchema(BasePaymentSchema):
    """
Schema for filtering payment methods"""
    user_id: Optional[int] = None
    method_type: Optional[PaymentMethodTypeEnum] = None
    provider: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class AnalyticsQuerySchema(BasePaymentSchema):
    """
Schema for analytics queries"""
    user_id: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    currency: Optional[CurrencyEnum] = None
    group_by: Optional[str] = Field(None, regex=r'^(day|week|month|quarter|year)$')
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


# Bulk Operation Schemas
class BulkPaymentTransactionSchema(BasePaymentSchema):
    """
Schema for bulk payment transaction operations"""
    transactions: List[PaymentTransactionCreateSchema] = Field(..., min_items=1, max_items=100)


class BulkPayoutSchema(BasePaymentSchema):
    """
Schema for bulk payout operations"""
    payouts: List[AutomatedPayoutCreateSchema] = Field(..., min_items=1, max_items=50)


# Error and Response Schemas
class PaymentErrorSchema(BasePaymentSchema):
    """
Schema for payment processing errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None


class PaymentSuccessSchema(BasePaymentSchema):
    """
Schema for successful payment responses"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


# Configuration Schemas
class PaymentConfigurationSchema(BasePaymentSchema):
    """
Schema for payment configuration"""
    default_currency: CurrencyEnum = CurrencyEnum.EUR
    supported_payment_methods: List[PaymentMethodTypeEnum]
    minimum_payout_amount: Decimal = Field(Decimal('50.00'), gt=0)
    payout_frequencies: List[str] = ["weekly", "monthly", "quarterly"]
    fee_structure: Dict[str, Decimal]
    tax_rates: Dict[str, Decimal]
