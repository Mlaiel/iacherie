"""
📊 Data Models - IA Influencer Agent Platform Enterprise  
=========================================================
Module: backend/data_management/models/revenue_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Data Models - Production-Ready
Responsibility: Revenue and monetization data models
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching → Multi-platform distribution → Revenue Generation

REVENUE MODEL ARCHITECTURE:
Revenue Tracking → Platform Integration → Payment Processing → 
Tax Calculations → Currency Exchange → Performance Analytics → Automated Payouts
"""

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import uuid

class RevenueType(Enum):
    """Revenue stream types"""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    SYNC_LICENSING = "sync_licensing"
    ROYALTIES = "royalties"
    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    NFT_SALES = "nft_sales"
    CROWDFUNDING = "crowdfunding"

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
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"
    HUF = "HUF"
    BGN = "BGN"
    RON = "RON"
    HRK = "HRK"

@dataclass
class RevenueModel:
    """Main revenue tracking model"""
    revenue_id: str = field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    content_id: str = ""
    platform: str = ""
    revenue_type: RevenueType = RevenueType.STREAMING
    
    # Financial data
    gross_amount: Decimal = field(default=Decimal('0.00'))
    currency: Currency = Currency.EUR
    exchange_rate: Decimal = field(default=Decimal('1.00'))
    net_amount: Decimal = field(default=Decimal('0.00'))
    
    # Fees and deductions
    platform_fee: Decimal = field(default=Decimal('0.00'))
    service_fee: Decimal = field(default=Decimal('0.00'))
    tax_amount: Decimal = field(default=Decimal('0.00'))
    payout_amount: Decimal = field(default=Decimal('0.00'))
    
    # Timestamps
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Payment tracking
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    payment_reference: Optional[str] = None
    
    # Metadata and analytics
    metadata: Dict[str, Any] = field(default_factory=dict)
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    
    # Audit fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Validation and flags
    is_verified: bool = False
    is_disputed: bool = False
    dispute_reason: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation and calculations"""
        # Ensure decimals are properly formatted
        self.gross_amount = Decimal(str(self.gross_amount)).quantize(Decimal('0.01'))
        self.net_amount = Decimal(str(self.net_amount)).quantize(Decimal('0.01'))
        self.platform_fee = Decimal(str(self.platform_fee)).quantize(Decimal('0.01'))
        self.service_fee = Decimal(str(self.service_fee)).quantize(Decimal('0.01'))
        self.tax_amount = Decimal(str(self.tax_amount)).quantize(Decimal('0.01'))
        self.payout_amount = Decimal(str(self.payout_amount)).quantize(Decimal('0.01'))
        self.exchange_rate = Decimal(str(self.exchange_rate)).quantize(Decimal('0.0001'))
        
        # Validate financial data consistency
        calculated_net = self.gross_amount - self.platform_fee - self.service_fee
        if abs(calculated_net - self.net_amount) > Decimal('0.01'):
            self.net_amount = calculated_net
        
        # Calculate payout amount if not set
        if self.payout_amount == Decimal('0.00'):
            self.payout_amount = self.net_amount - self.tax_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'revenue_id': self.revenue_id,
            'creator_id': self.creator_id,
            'content_id': self.content_id,
            'platform': self.platform,
            'revenue_type': self.revenue_type.value,
            'gross_amount': str(self.gross_amount),
            'currency': self.currency.value,
            'exchange_rate': str(self.exchange_rate),
            'net_amount': str(self.net_amount),
            'platform_fee': str(self.platform_fee),
            'service_fee': str(self.service_fee),
            'tax_amount': str(self.tax_amount),
            'payout_amount': str(self.payout_amount),
            'timestamp': self.timestamp.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'payment_status': self.payment_status.value,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'transaction_id': self.transaction_id,
            'payment_reference': self.payment_reference,
            'metadata': self.metadata,
            'analytics_data': self.analytics_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_verified': self.is_verified,
            'is_disputed': self.is_disputed,
            'dispute_reason': self.dispute_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RevenueModel':
        """Create instance from dictionary"""
        # Convert string timestamps back to datetime objects
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        if 'period_start' in data and isinstance(data['period_start'], str):
            data['period_start'] = datetime.fromisoformat(data['period_start'].replace('Z', '+00:00'))
        if 'period_end' in data and isinstance(data['period_end'], str):
            data['period_end'] = datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        if 'payment_date' in data and data['payment_date'] and isinstance(data['payment_date'], str):
            data['payment_date'] = datetime.fromisoformat(data['payment_date'].replace('Z', '+00:00'))
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        # Convert enum values
        if 'revenue_type' in data and isinstance(data['revenue_type'], str):
            data['revenue_type'] = RevenueType(data['revenue_type'])
        if 'currency' in data and isinstance(data['currency'], str):
            data['currency'] = Currency(data['currency'])
        if 'payment_status' in data and isinstance(data['payment_status'], str):
            data['payment_status'] = PaymentStatus(data['payment_status'])
        
        # Convert decimal values
        decimal_fields = ['gross_amount', 'exchange_rate', 'net_amount', 'platform_fee', 
                         'service_fee', 'tax_amount', 'payout_amount']
        for field_name in decimal_fields:
            if field_name in data and isinstance(data[field_name], (str, int, float)):
                data[field_name] = Decimal(str(data[field_name]))
        
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate model data and return list of errors"""
        errors = []
        
        if not self.revenue_id:
            errors.append("Revenue ID is required")
        
        if not self.creator_id:
            errors.append("Creator ID is required")
        
        if not self.content_id:
            errors.append("Content ID is required")
        
        if not self.platform:
            errors.append("Platform is required")
        
        if self.gross_amount < Decimal('0'):
            errors.append("Gross amount cannot be negative")
        
        if self.net_amount < Decimal('0'):
            errors.append("Net amount cannot be negative")
        
        if self.period_start > self.period_end:
            errors.append("Period start must be before period end")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if model is valid"""
        return len(self.validate()) == 0
    
    def calculate_effective_rate(self) -> Decimal:
        """Calculate effective revenue rate after all fees"""
        if self.gross_amount == 0:
            return Decimal('0.00')
        
        return (self.payout_amount / self.gross_amount * 100).quantize(Decimal('0.01'))
    
    def get_fee_breakdown(self) -> Dict[str, Decimal]:
        """Get detailed fee breakdown"""
        return {
            'platform_fee': self.platform_fee,
            'service_fee': self.service_fee,
            'tax_amount': self.tax_amount,
            'total_fees': self.platform_fee + self.service_fee + self.tax_amount,
            'net_rate': self.calculate_effective_rate()
        }

@dataclass
class RevenueSummaryModel:
    """Revenue summary for analytics and reporting"""
    summary_id: str = field(default_factory=lambda: f"summary_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Financial totals
    total_gross: Decimal = field(default=Decimal('0.00'))
    total_net: Decimal = field(default=Decimal('0.00'))
    total_fees: Decimal = field(default=Decimal('0.00'))
    total_taxes: Decimal = field(default=Decimal('0.00'))
    total_payout: Decimal = field(default=Decimal('0.00'))
    currency: Currency = Currency.EUR
    
    # Breakdown by revenue type
    revenue_by_type: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_platform: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_content: Dict[str, Decimal] = field(default_factory=dict)
    
    # Performance metrics
    growth_rate: float = 0.0
    average_revenue_per_content: Decimal = field(default=Decimal('0.00'))
    top_performing_content: List[str] = field(default_factory=list)
    top_platforms: List[str] = field(default_factory=list)
    
    # Analytics data
    total_transactions: int = 0
    unique_platforms: int = 0
    unique_content_items: int = 0
    
    # Timestamps
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Post-initialization calculations"""
        # Ensure decimals are properly formatted
        self.total_gross = Decimal(str(self.total_gross)).quantize(Decimal('0.01'))
        self.total_net = Decimal(str(self.total_net)).quantize(Decimal('0.01'))
        self.total_fees = Decimal(str(self.total_fees)).quantize(Decimal('0.01'))
        self.total_taxes = Decimal(str(self.total_taxes)).quantize(Decimal('0.01'))
        self.total_payout = Decimal(str(self.total_payout)).quantize(Decimal('0.01'))
        self.average_revenue_per_content = Decimal(str(self.average_revenue_per_content)).quantize(Decimal('0.01'))
        
        # Convert revenue breakdowns to Decimal
        self.revenue_by_type = {k: Decimal(str(v)).quantize(Decimal('0.01')) 
                               for k, v in self.revenue_by_type.items()}
        self.revenue_by_platform = {k: Decimal(str(v)).quantize(Decimal('0.01')) 
                                   for k, v in self.revenue_by_platform.items()}
        self.revenue_by_content = {k: Decimal(str(v)).quantize(Decimal('0.01')) 
                                  for k, v in self.revenue_by_content.items()}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'summary_id': self.summary_id,
            'creator_id': self.creator_id,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_gross': str(self.total_gross),
            'total_net': str(self.total_net),
            'total_fees': str(self.total_fees),
            'total_taxes': str(self.total_taxes),
            'total_payout': str(self.total_payout),
            'currency': self.currency.value,
            'revenue_by_type': {k: str(v) for k, v in self.revenue_by_type.items()},
            'revenue_by_platform': {k: str(v) for k, v in self.revenue_by_platform.items()},
            'revenue_by_content': {k: str(v) for k, v in self.revenue_by_content.items()},
            'growth_rate': self.growth_rate,
            'average_revenue_per_content': str(self.average_revenue_per_content),
            'top_performing_content': self.top_performing_content,
            'top_platforms': self.top_platforms,
            'total_transactions': self.total_transactions,
            'unique_platforms': self.unique_platforms,
            'unique_content_items': self.unique_content_items,
            'generated_at': self.generated_at.isoformat()
        }

@dataclass
class PaymentRequestModel:
    """Payment request tracking model"""
    request_id: str = field(default_factory=lambda: f"pay_{uuid.uuid4().hex[:12]}")
    creator_id: str = ""
    amount: Decimal = field(default=Decimal('0.00'))
    currency: Currency = Currency.EUR
    payment_method: str = ""
    
    # Recipient details
    recipient_details: Dict[str, Any] = field(default_factory=dict)
    
    # Status tracking
    status: PaymentStatus = PaymentStatus.PENDING
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Transaction details
    transaction_id: Optional[str] = None
    external_reference: Optional[str] = None
    processor_response: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    failure_reason: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Revenue entries included in this payment
    revenue_entries: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        self.amount = Decimal(str(self.amount)).quantize(Decimal('0.01'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'request_id': self.request_id,
            'creator_id': self.creator_id,
            'amount': str(self.amount),
            'currency': self.currency.value,
            'payment_method': self.payment_method,
            'recipient_details': self.recipient_details,
            'status': self.status.value,
            'requested_at': self.requested_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'transaction_id': self.transaction_id,
            'external_reference': self.external_reference,
            'processor_response': self.processor_response,
            'failure_reason': self.failure_reason,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'revenue_entries': self.revenue_entries,
            'metadata': self.metadata
        }
    
    def can_retry(self) -> bool:
        """Check if payment can be retried"""
        return (self.status == PaymentStatus.FAILED and 
                self.retry_count < self.max_retries)
    
    def mark_failed(self, reason: str):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.retry_count += 1
    
    def mark_completed(self, transaction_id: str):
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.completed_at = datetime.now(timezone.utc)

@dataclass
class PlatformConfigModel:
    """Platform configuration for revenue calculations"""
    platform_id: str = ""
    platform_name: str = ""
    
    # Fee structure
    platform_fee_rate: Decimal = field(default=Decimal('0.30'))  # 30%
    minimum_payout: Decimal = field(default=Decimal('25.00'))
    payout_frequency: str = "monthly"  # daily, weekly, monthly
    
    # API configuration
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    
    # Rate limiting
    rate_limit_requests_per_hour: int = 100
    max_concurrent_requests: int = 5
    
    # Currency support
    supported_currencies: List[Currency] = field(default_factory=lambda: [Currency.EUR, Currency.USD])
    
    # Revenue types supported
    supported_revenue_types: List[RevenueType] = field(default_factory=lambda: [RevenueType.STREAMING])
    
    # Metadata
    is_active: bool = True
    last_sync: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        self.platform_fee_rate = Decimal(str(self.platform_fee_rate)).quantize(Decimal('0.0001'))
        self.minimum_payout = Decimal(str(self.minimum_payout)).quantize(Decimal('0.01'))

# Export all models
__all__ = [
    'RevenueModel',
    'RevenueSummaryModel', 
    'PaymentRequestModel',
    'PlatformConfigModel',
    'RevenueType',
    'PaymentStatus',
    'Currency'
]
